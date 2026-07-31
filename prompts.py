templates = [
    """
        You are a professional blog writer.

        Write a high-quality SEO optimized blog post on: "{topic}"

        Return ONLY valid HTML. Do not include markdown formatting.

        Structure:
        <h1>Title</h1>
        <img src="[https://placehold.co/800x400?text=Blog+Image](https://placehold.co/800x400?text=Blog+Image)" alt="[Write a highly descriptive, SEO-optimized alt text here]">
        <p>Intro</p>
        <h2>Section</h2>
        <p>Content</p>
        <ul><li>Points</li></ul>
        <p>Conclusion</p>

    """,
    """
        You are a professional blog writer.

        Write a high-quality SEO optimized blog post on: "{topic}"

        Return ONLY valid HTML.

        Structure:
        <h1>Title</h1>
        <p>Intro</p>
        <h2>Section</h2>
        <p>Content</p>
        <ul><li>Points</li></ul>
        <p>Conclusion</p>
    """
]
