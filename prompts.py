templates = [
    """
        You are a professional, expert SEO blog writer and content strategist.

        Write a comprehensive, high-quality, and SEO-optimized blog post on the topic: "{topic}"

        CRITICAL REQUIREMENTS:
        1. Length: The post MUST contain a minimum of 700 words. To achieve this, do not just scratch the surface. Provide deep analysis, actionable insights, detailed explanations, and elaborate fully on every point.
        2. Structure: Write at least 4 to 5 main sections to ensure depth.
        3. Format: Return ONLY raw, valid HTML. Do NOT wrap your response in markdown code blocks (e.g., do not use ```html). Start immediately with the <h1> tag and end with the final closing tag.

        Follow this exact HTML structure, expanding heavily on the content to meet the length requirement:

        <h1>[Engaging, Click-Worthy SEO Title]</h1>

        <img src="https://placehold.co/800x400?text=Blog+Image" alt="[Write a highly descriptive, SEO-optimized alt text here]">

        <p>[A captivating introduction that hooks the reader, clearly explains the value of the article, and includes primary keywords. (Write at least 100 words here)]</p>

        <h2>[First Main Section Title]</h2>
        <p>[Detailed, multi-sentence paragraph explaining the concept...]</p>
        <p>[Follow-up paragraph with deeper insights...]</p>

        <h2>[Second Main Section Title]</h2>
        <p>[Detailed content...]</p>
        <ul>
            <li><strong>[Key Point 1]:</strong> [In-depth explanation of this point]</li>
            <li><strong>[Key Point 2]:</strong> [In-depth explanation of this point]</li>
            <li><strong>[Key Point 3]:</strong> [In-depth explanation of this point]</li>
        </ul>

        <h2>[Third Main Section Title]</h2>
        <p>[Detailed content...]</p>
        <h3>[Relevant Subsection Title]</h3>
        <p>[Granular details, examples, or case studies to add immense value...]</p>

        <h2>[Fourth Main Section Title]</h2>
        <p>[Detailed content...]</p>

        <h2>Conclusion</h2>
        <p>[A strong wrap-up summarizing the core takeaways, followed by an engaging call to action asking the reader to share their thoughts or take the next step.]</p>
    """
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
