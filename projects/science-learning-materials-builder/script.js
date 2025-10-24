// Sample topic buttons
const sampleButtons = document.querySelectorAll('.sample-btn');
const scienceTopic = document.getElementById('scienceTopic');

sampleButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        const topic = btn.getAttribute('data-topic');
        scienceTopic.value = topic;
        scienceTopic.focus();
    });
});

// Form submission
const lessonForm = document.getElementById('lessonForm');
const submitBtn = document.getElementById('submitBtn');
const loadingSpinner = document.getElementById('loadingSpinner');
const agentProgress = document.getElementById('agentProgress');
const resultsSection = document.getElementById('resultsSection');

lessonForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    // Get form data
    const topic = scienceTopic.value.trim();
    const gradeLevel = parseInt(document.getElementById('gradeLevel').value);
    const duration = parseInt(document.getElementById('lessonDuration').value);
    const model = document.getElementById('modelName').value;
    const includeImages = document.getElementById('includeImages').checked;
    const includeQuiz = document.getElementById('includeQuiz').checked;
    const includeActivity = document.getElementById('includeActivity').checked;
    const webResearch = document.getElementById('webResearch').checked;

    // Validate
    if (!topic) {
        alert('Please enter a science topic or question');
        return;
    }

    // Show loading and agent progress
    loadingSpinner.style.display = 'block';
    agentProgress.style.display = 'block';
    resultsSection.style.display = 'none';
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating Lesson...';

    try {
        // Simulate agent workflow
        await simulateAgentWorkflow(topic, gradeLevel, duration, {
            model,
            includeImages,
            includeQuiz,
            includeActivity,
            webResearch
        });

        // Prepare request
        const requestData = {
            topic: topic,
            grade_level: gradeLevel,
            duration: duration,
            model_name: model,
            include_images: includeImages,
            include_quiz: includeQuiz,
            include_activity: includeActivity,
            web_research: webResearch
        };

        // Make API call (replace with your backend endpoint)
        const response = await fetch('/api/generate-lesson', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();

        // Display results
        displayResults(result);

    } catch (error) {
        console.error('Error:', error);

        // For demo mode, generate mock results
        if (window.location.search.includes('demo=true') || error.message.includes('Failed to fetch')) {
            const mockResult = generateMockLesson(topic, gradeLevel);
            displayResults(mockResult);
        } else {
            displayError(error.message);
        }
    } finally {
        loadingSpinner.style.display = 'none';
        agentProgress.style.display = 'none';
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-magic"></i> Generate Lesson Plan';
    }
});

async function simulateAgentWorkflow(topic, gradeLevel, duration, options) {
    // Agent 1: Curriculum Research
    await updateAgentStatus('agent1', 'active', 'Researching topic and validating age-appropriateness...');
    await delay(2000);
    await updateAgentStatus('agent1', 'completed', 'Completed research and curriculum validation');

    // Agent 2: Visual Illustrator
    if (options.includeImages) {
        await updateAgentStatus('agent2', 'active', 'Generating image prompts for educational visuals...');
        await delay(1500);
        await updateAgentStatus('agent2', 'completed', 'Created 3 educational illustration prompts');
    } else {
        await updateAgentStatus('agent2', 'completed', 'Skipped (images disabled)');
    }

    // Agent 3: Content Writer
    await updateAgentStatus('agent3', 'active', 'Writing lesson content and quiz questions...');
    await delay(2000);
    await updateAgentStatus('agent3', 'completed', 'Created lesson content and assessments');

    // Agent 4: Lesson Packaging
    await updateAgentStatus('agent4', 'active', 'Packaging complete lesson plan...');
    await delay(1000);
    await updateAgentStatus('agent4', 'completed', 'Lesson plan ready for download');
}

function updateAgentStatus(agentId, status, message) {
    const agent = document.getElementById(agentId);
    const info = agent.querySelector('.agent-info p');
    const check = agent.querySelector('.agent-check i');

    info.textContent = message;

    if (status === 'active') {
        agent.classList.add('active');
        agent.classList.remove('completed');
        check.className = 'fas fa-spinner fa-spin';
    } else if (status === 'completed') {
        agent.classList.remove('active');
        agent.classList.add('completed');
        check.className = 'fas fa-check-circle';
    }

    return Promise.resolve();
}

function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function displayResults(result) {
    resultsSection.style.display = 'block';

    // Summary
    const summaryContent = document.getElementById('summaryContent');
    summaryContent.innerHTML = `
        <p><strong>Topic:</strong> ${result.topic}</p>
        <p><strong>Grade Level:</strong> ${result.grade_level} (Ages ${result.grade_level + 5}-${result.grade_level + 6})</p>
        <p><strong>Duration:</strong> ${result.duration || 45} minutes</p>
        <p><strong>Category:</strong> ${result.category || 'General Science'}</p>
        <p><strong>Generated:</strong> ${new Date().toLocaleString()}</p>
    `;

    // Teacher Guide
    const teacherContent = document.getElementById('teacherContent');
    teacherContent.innerHTML = formatMarkdown(result.teacher_guide || result.topic_summary);

    // Student Lesson
    const studentContent = document.getElementById('studentContent');
    studentContent.innerHTML = formatMarkdown(result.lesson_content?.explanation || 'Explanation not available');

    // Visual Materials
    const visualContent = document.getElementById('visualContent');
    if (result.images && Object.keys(result.images).length > 0) {
        let visualHTML = '';
        for (const [key, value] of Object.entries(result.images)) {
            visualHTML += `
                <div class="visual-item">
                    <div class="visual-title">${formatVisualTitle(key)}</div>
                    <div class="visual-description"><strong>Caption:</strong> ${value.caption}</div>
                    <div class="visual-description"><strong>Prompt:</strong> ${value.prompt}</div>
                </div>
            `;
        }
        visualContent.innerHTML = visualHTML;
    } else {
        document.getElementById('visualSection').style.display = 'none';
    }

    // Vocabulary
    const vocabularyContent = document.getElementById('vocabularyContent');
    if (result.lesson_content?.vocabulary && result.lesson_content.vocabulary.length > 0) {
        let vocabHTML = '';
        result.lesson_content.vocabulary.forEach(item => {
            vocabHTML += `
                <div class="vocab-item">
                    <div class="vocab-term">${item.term}</div>
                    <div class="vocab-definition">${item.definition}</div>
                </div>
            `;
        });
        vocabularyContent.innerHTML = vocabHTML;
    } else {
        document.getElementById('vocabularySection').style.display = 'none';
    }

    // Quiz Questions
    const quizContent = document.getElementById('quizContent');
    if (result.lesson_content?.multiple_choice || result.lesson_content?.short_answer) {
        let quizHTML = '<h4>Multiple Choice Questions</h4>';

        if (result.lesson_content.multiple_choice) {
            result.lesson_content.multiple_choice.forEach((q, idx) => {
                quizHTML += `
                    <div class="quiz-question">
                        <strong>${idx + 1}. ${q.question}</strong>
                        <div class="quiz-options">
                            ${q.options.map(opt => `<div>${opt}</div>`).join('')}
                        </div>
                        <div style="margin-top:10px; color:#10b981;"><strong>Answer: ${q.correct_answer}</strong></div>
                    </div>
                `;
            });
        }

        if (result.lesson_content.short_answer) {
            quizHTML += '<h4 style="margin-top:20px;">Short Answer Questions</h4>';
            result.lesson_content.short_answer.forEach((q, idx) => {
                quizHTML += `
                    <div class="quiz-question">
                        <strong>${idx + 1}. ${q.question}</strong>
                        <div style="margin-top:10px;"><strong>Sample Answer:</strong> ${q.sample_answer}</div>
                    </div>
                `;
            });
        }

        quizContent.innerHTML = quizHTML;
    } else {
        document.getElementById('quizSection').style.display = 'none';
    }

    // Fun Challenge
    const activityContent = document.getElementById('activityContent');
    if (result.lesson_content?.fun_challenge) {
        activityContent.innerHTML = formatMarkdown(result.lesson_content.fun_challenge);
    } else {
        document.getElementById('activitySection').style.display = 'none';
    }

    // Store result for download
    window.currentLesson = result;

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function formatMarkdown(text) {
    if (!text) return '';

    return text
        .replace(/\n/g, '<br>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/### (.*?)(<br>|$)/g, '<h4>$1</h4>')
        .replace(/## (.*?)(<br>|$)/g, '<h3>$1</h3>')
        .replace(/# (.*?)(<br>|$)/g, '<h2>$1</h2>');
}

function formatVisualTitle(key) {
    const titles = {
        'diagram': 'Educational Diagram',
        'fun_illustration': 'Fun Illustration',
        'process': 'Process Steps'
    };
    return titles[key] || key;
}

function displayError(message) {
    resultsSection.style.display = 'block';

    const summaryContent = document.getElementById('summaryContent');
    summaryContent.innerHTML = `
        <div style="color: #dc2626; padding: 20px; background: #fef2f2; border-radius: 8px; border: 2px solid #fca5a5;">
            <h3><i class="fas fa-exclamation-triangle"></i> Error</h3>
            <p>${message}</p>
            <p style="margin-top: 10px;">Please check your API keys and try again. For demo mode, add <code>?demo=true</code> to the URL.</p>
        </div>
    `;

    // Hide other sections
    document.getElementById('teacherGuide').style.display = 'none';
    document.getElementById('studentLesson').style.display = 'none';
    document.getElementById('visualSection').style.display = 'none';
    document.getElementById('vocabularySection').style.display = 'none';
    document.getElementById('quizSection').style.display = 'none';
    document.getElementById('activitySection').style.display = 'none';
    document.querySelector('.download-section').style.display = 'none';

    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function generateMockLesson(topic, gradeLevel) {
    return {
        topic: topic,
        grade_level: gradeLevel,
        duration: 45,
        category: 'Science',
        topic_summary: `This lesson teaches students about ${topic}. It covers the fundamental concepts in an age-appropriate way using hands-on activities and visual aids.`,
        teacher_guide: `### Learning Objectives\n- Understand the basic concepts of ${topic}\n- Identify key components and processes\n- Apply knowledge to real-world examples\n\n### Key Concepts\n- Main idea explained simply\n- Supporting details and examples\n- Connections to everyday life\n\n### Teaching Tips\n- Start with a fun question or demonstration\n- Use visual aids and hands-on activities\n- Encourage student questions and discussion`,
        images: {
            diagram: {
                caption: `Educational diagram showing ${topic}`,
                prompt: `Create a clear, labeled educational diagram illustrating ${topic} for elementary school students`
            },
            fun_illustration: {
                caption: `Fun cartoon illustration of ${topic}`,
                prompt: `Create a colorful, engaging cartoon-style illustration of ${topic} that will excite 9-year-old students`
            },
            process: {
                caption: `Step-by-step process of ${topic}`,
                prompt: `Create a step-by-step visual guide showing the process of ${topic} in simple, numbered steps`
            }
        },
        lesson_content: {
            explanation: `Have you ever wondered about ${topic}? It's actually really cool! Let me tell you about it.\n\nFirst, you need to know that this happens all around us. You might not see it, but it's there! The main idea is simple. Things work together in a special way.\n\nScientists have studied this for a long time. They discovered some amazing facts. Now we understand how it works!\n\nThis is important because it affects our daily lives. Without this, things would be very different. Isn't that fascinating?`,
            vocabulary: [
                {
                    term: 'Key Term 1',
                    definition: 'A simple explanation that a 9-year-old can understand'
                },
                {
                    term: 'Key Term 2',
                    definition: 'Another important word explained in kid-friendly language'
                },
                {
                    term: 'Key Term 3',
                    definition: 'The last main vocabulary word with an easy definition'
                }
            ],
            multiple_choice: [
                {
                    question: `What is the main idea of ${topic}?`,
                    options: ['A. First option', 'B. Correct answer', 'C. Third option', 'D. Fourth option'],
                    correct_answer: 'B'
                },
                {
                    question: 'Why is this important?',
                    options: ['A. It helps us understand nature', 'B. It looks pretty', 'C. Scientists like it', 'D. It makes noise'],
                    correct_answer: 'A'
                },
                {
                    question: 'Where can you find this happening?',
                    options: ['A. Only in labs', 'B. In space', 'C. All around us', 'D. Nowhere'],
                    correct_answer: 'C'
                }
            ],
            short_answer: [
                {
                    question: `Explain in your own words how ${topic} works.`,
                    sample_answer: 'Student should describe the main process in simple language, mentioning key components and steps.'
                },
                {
                    question: `Give an example of ${topic} in everyday life.`,
                    sample_answer: 'Student should provide a real-world example they can observe or experience.'
                }
            ],
            fun_challenge: `Try this fun activity at home! Create a simple model or experiment that demonstrates ${topic}. You can use household items like paper, plastic containers, or food coloring. Draw what happens and share with your class!`
        }
    };
}

// Download handlers
document.getElementById('downloadMarkdown')?.addEventListener('click', () => {
    if (!window.currentLesson) return;

    const markdown = generateMarkdownContent(window.currentLesson);
    const blob = new Blob([markdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `science_lesson_${sanitizeFilename(window.currentLesson.topic)}.md`;
    a.click();
    URL.revokeObjectURL(url);
});

document.getElementById('downloadPDF')?.addEventListener('click', () => {
    alert('PDF download requires backend processing. Please use the Python script or Google Colab notebook for PDF generation.');
});

document.getElementById('printLesson')?.addEventListener('click', () => {
    window.print();
});

function generateMarkdownContent(lesson) {
    let content = `# 🔬 Science Lesson: ${lesson.topic}\n\n`;
    content += `**Grade Level**: ${lesson.grade_level} (Ages ${lesson.grade_level + 5}-${lesson.grade_level + 6})\n`;
    content += `**Duration**: ${lesson.duration || 45} minutes\n`;
    content += `**Category**: ${lesson.category || 'Science'}\n\n`;
    content += `---\n\n## 📚 Teacher Guide\n\n${lesson.teacher_guide}\n\n`;
    content += `---\n\n## 📖 Student Lesson\n\n${lesson.lesson_content?.explanation}\n\n`;

    if (lesson.lesson_content?.vocabulary) {
        content += `### 📝 Vocabulary\n\n`;
        lesson.lesson_content.vocabulary.forEach(v => {
            content += `**${v.term}**: ${v.definition}\n\n`;
        });
    }

    content += `---\n\n## ✅ Quiz Questions\n\n`;

    if (lesson.lesson_content?.multiple_choice) {
        content += `### Multiple Choice\n\n`;
        lesson.lesson_content.multiple_choice.forEach((q, i) => {
            content += `**${i + 1}. ${q.question}**\n\n`;
            q.options.forEach(opt => content += `   ${opt}\n`);
            content += `\n   **Answer: ${q.correct_answer}**\n\n`;
        });
    }

    if (lesson.lesson_content?.short_answer) {
        content += `### Short Answer\n\n`;
        lesson.lesson_content.short_answer.forEach((q, i) => {
            content += `**${i + 1}. ${q.question}**\n\n`;
            content += `Sample Answer: ${q.sample_answer}\n\n`;
        });
    }

    if (lesson.lesson_content?.fun_challenge) {
        content += `---\n\n## 🌟 Fun Challenge\n\n${lesson.lesson_content.fun_challenge}\n\n`;
    }

    content += `---\n\n*Generated: ${new Date().toLocaleString()}*\n`;

    return content;
}

function sanitizeFilename(name) {
    return name.replace(/[^a-z0-9]/gi, '_').toLowerCase();
}

// Reset agent status when form is shown
function resetAgentStatus() {
    const agents = ['agent1', 'agent2', 'agent3', 'agent4'];
    agents.forEach(agentId => {
        const agent = document.getElementById(agentId);
        agent.classList.remove('active', 'completed');
        const check = agent.querySelector('.agent-check i');
        check.className = 'fas fa-clock';
        const info = agent.querySelector('.agent-info p');
        info.textContent = 'Waiting...';
    });
}

// Initialize
console.log('Science Learning Materials Builder loaded!');
console.log('Add ?demo=true to URL for demo mode without backend');
