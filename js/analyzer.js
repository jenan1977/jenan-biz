// Intelligent Project Analyzer Robot

class ProjectAnalyzer {
    constructor(projectName) {
        this.projectName = projectName;
        this.analysisReport = '';
    }

    askQuestions() {
        return [
            `What are the main objectives of the ${this.projectName}?`,
            `Who are the stakeholders involved in the ${this.projectName}?`,
            `What resources are available for the ${this.projectName}?`,
            `What are the potential risks associated with the ${this.projectName}?`
        ];
    }

    generateReport(answers) {
        this.analysisReport = `Analysis Report for ${this.projectName}\n` +
                              `-----------------------------------\n` +
                              `Objectives: ${answers[0]}\n` +
                              `Stakeholders: ${answers[1]}\n` +
                              `Resources: ${answers[2]}\n` +
                              `Risks: ${answers[3]}\n`; 
        return this.analysisReport;
    }
}

// Example usage:
const analyzer = new ProjectAnalyzer('New Website Launch');
const questions = analyzer.askQuestions();
console.log(questions);

// Assuming answers are collected somehow 
// const answers = ['Increase traffic', 'Marketing team', 'Budget, Developers', 'Delayed launch'];
// console.log(analyzer.generateReport(answers));
