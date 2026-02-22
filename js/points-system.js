// points-system.js

class PointsSystem {
    constructor() {
        this.users = {};
        this.referrals = {};
    }

    // Method to add points to a user
    addPoints(userId, points) {
        if (!this.users[userId]) {
            this.users[userId] = { points: 0, referrals: [], stats: {} };
        }
        this.users[userId].points += points;
    }

    // Method to handle referrals
    referUser(referrerId, referredId) {
        if (!this.referrals[referrerId]) {
            this.referrals[referrerId] = [];
        }
        this.referrals[referrerId].push(referredId);
        this.addPoints(referrerId, 10); // Reward referrer with points
        this.addPoints(referredId, 5); // Reward referred user with points
    }

    // Method to get user statistics
    getUserStats(userId) {
        return this.users[userId] ? this.users[userId].stats : null;
    }

    // Method to set/retrieve user statistics
    setUserStats(userId, stats) {
        if (this.users[userId]) {
            this.users[userId].stats = stats;
        }
    }

    // Method to get total points of a user
    getTotalPoints(userId) {
        return this.users[userId] ? this.users[userId].points : 0;
    }
}

// Example usage:
// const ps = new PointsSystem();
// ps.addPoints('user1', 100);
// ps.referUser('user2', 'user3');