// blog-post.js

// Function to fetch article by ID
async function fetchArticle(articleId) {
    try {
        const response = await fetch(`https://api.example.com/articles/${articleId}`);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const article = await response.json();
        return article;
    } catch (error) {
        console.error('Error fetching article:', error);
    }
}

// Function to display article and related content
async function displayArticle(articleId) {
    const article = await fetchArticle(articleId);
    if (article) {
        document.title = article.title;
        const articleContainer = document.getElementById('article-container');
        articleContainer.innerHTML = `<h1>${article.title}</h1><p>${article.content}</p>`;

        // Display related content
        const relatedContainer = document.getElementById('related-content');
        relatedContainer.innerHTML = '<h2>Related Articles</h2>';

        article.related.forEach(rel => {
            relatedContainer.innerHTML += `<div><h3>${rel.title}</h3><p>${rel.summary}</p></div>`;
        });
    }
}

// Example usage: displayArticle('article-id-123');
