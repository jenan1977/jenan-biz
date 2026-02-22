// Daily Courses System

class Course {
    constructor(title, lessons = [], quizzes = [], certificates = []) {
        this.title = title;
        this.lessons = lessons; // Array of lesson objects
        this.quizzes = quizzes; // Array of quiz objects
        this.certificates = certificates; // Array of certificates
        this.points = 0; // Points earned by the user
    }

    addLesson(lesson) {
        this.lessons.push(lesson);
    }

    addQuiz(quiz) {
        this.quizzes.push(quiz);
    }

    addCertificate(certificate) {
        this.certificates.push(certificate);
    }

    earnPoints(points) {
        this.points += points;
    }

    getCourseInfo() {
        return {
            title: this.title,
            lessons: this.lessons,
            quizzes: this.quizzes,
            certificates: this.certificates,
            points: this.points
        };
    }
}

// Example Usage:
const jsCourse = new Course('JavaScript Basics');
jsCourse.addLesson('Intro to JavaScript');
jsCourse.addQuiz('JS Fundamentals Quiz');
jsCourse.earnPoints(10);

console.log(jsCourse.getCourseInfo());