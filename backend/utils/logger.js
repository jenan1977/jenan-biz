/**
 * logger.js – Winston-based structured logger.
 *
 * Writes to:
 *  - Console (all levels in development, warn+ in production)
 *  - logs/combined.log  – all messages
 *  - logs/error.log     – error messages only
 *  - logs/requests.log  – HTTP request entries (written from middleware)
 */

"use strict";

const path = require("path");
const { createLogger, format, transports } = require("winston");
const config = require("../config");

const { combine, timestamp, errors, json, colorize, printf } = format;

const logDir = path.resolve(config.LOG_DIR);

// ── Formats ─────────────────────────────────────────────────────────────────

const devFormat = combine(
  colorize(),
  timestamp({ format: "HH:mm:ss" }),
  errors({ stack: true }),
  printf(({ level, message, timestamp: ts, stack, ...meta }) => {
    const extras = Object.keys(meta).length ? " " + JSON.stringify(meta) : "";
    return `${ts} [${level}] ${stack || message}${extras}`;
  })
);

const prodFormat = combine(timestamp(), errors({ stack: true }), json());

const activeFormat = config.NODE_ENV === "production" ? prodFormat : devFormat;

// ── Logger instance ──────────────────────────────────────────────────────────

const logger = createLogger({
  level: config.LOG_LEVEL,
  format: activeFormat,
  transports: [
    // All logs
    new transports.File({ filename: path.join(logDir, "combined.log") }),
    // Errors only
    new transports.File({ filename: path.join(logDir, "error.log"), level: "error" }),
    // Console
    new transports.Console({
      level: config.NODE_ENV === "production" ? "warn" : config.LOG_LEVEL,
      format: activeFormat,
    }),
  ],
  exitOnError: false,
});

// ── Dedicated request logger ─────────────────────────────────────────────────

const requestLogger = createLogger({
  level: "info",
  format: combine(timestamp(), json()),
  transports: [
    new transports.File({ filename: path.join(logDir, "requests.log") }),
  ],
  exitOnError: false,
});

/**
 * Express middleware that logs each incoming HTTP request.
 *
 * @param {import('express').Request}  req
 * @param {import('express').Response} res
 * @param {import('express').NextFunction} next
 */
function requestLogMiddleware(req, res, next) {
  const start = Date.now();
  res.on("finish", () => {
    const durationMs = Date.now() - start;
    requestLogger.info("http_request", {
      method: req.method,
      url: req.originalUrl,
      status: res.statusCode,
      durationMs,
      ip: req.ip,
      userAgent: req.get("user-agent") || "",
    });
  });
  next();
}

logger.requestLogMiddleware = requestLogMiddleware;

module.exports = logger;
