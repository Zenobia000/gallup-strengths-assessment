-- =============================================================================
-- Gallup Strengths Assessment System - Comprehensive Seed Data
-- =============================================================================
-- This file contains all reference data needed for the assessment system:
-- - 34 Gallup Strength themes with detailed descriptions
-- - Mini-IPIP question bank for personality assessment
-- - Assessment configurations for different assessment types
-- - Lookup tables and reference data
-- =============================================================================

-- =============================================================================
-- GALLUP 34 STRENGTH THEMES
-- =============================================================================

-- EXECUTING DOMAIN STRENGTHS
INSERT INTO gallup_strengths (strength_name, theme, description, key_characteristics, development_suggestions, related_strengths, complementary_strengths, potential_blind_spots, leadership_application, team_contribution) VALUES

('Achiever', 'Executing', 'People exceptionally talented in the Achiever theme work hard and possess a great deal of stamina. They take immense satisfaction in being busy and productive.',
'["Driven by constant achievement", "High energy and stamina", "Deep satisfaction from productivity", "Strong work ethic", "Results-oriented mindset"]',
'["Set clear daily goals", "Track and celebrate accomplishments", "Partner with strategic thinkers", "Take breaks to avoid burnout", "Find meaning in work"]',
'["Discipline", "Focus", "Responsibility"]',
'["Strategic", "Maximizer", "Arranger"]',
'["May prioritize quantity over quality", "Risk of burnout from overwork", "Difficulty delegating tasks"]',
'Leaders with Achiever set the pace and model hard work, inspiring others through their dedication and consistent results.',
'Achievers drive team productivity, meet deadlines consistently, and maintain high energy levels that motivate others.'),

('Arranger', 'Executing', 'People exceptionally talented in the Arranger theme can organize, but they also have a flexibility that complements this ability. They like to determine how all of the pieces and resources can be arranged for maximum productivity.',
'["Natural organizer of people and resources", "Flexible and adaptive approach", "Systems thinking capability", "Coordination expertise", "Efficiency focused"]',
'["Practice scenario planning", "Develop contingency plans", "Learn project management tools", "Build networks of resources", "Embrace change as opportunity"]',
'["Discipline", "Responsibility", "Maximizer"]',
'["Strategic", "Command", "Activator"]',
'["May over-complicate simple situations", "Risk of changing plans too frequently", "Difficulty saying no to requests"]',
'Arranger leaders excel at resource allocation, crisis management, and creating efficient systems for their teams.',
'Arrangers optimize team workflows, coordinate complex projects, and adapt quickly to changing circumstances.'),

('Belief', 'Executing', 'People exceptionally talented in the Belief theme have certain core values that are unchanging. Out of these values emerges a defined purpose for their life.',
'["Strong core values system", "Unwavering sense of purpose", "Integrity in all actions", "Passionate about causes", "Reliable and consistent"]',
'["Articulate your values clearly", "Align work with purpose", "Seek mission-driven opportunities", "Be patient with different values", "Use values to guide decisions"]',
'["Consistency", "Responsibility", "Discipline"]',
'["Connectedness", "Empathy", "Developer"]',
'["May be inflexible with different viewpoints", "Risk of being judgmental", "Difficulty compromising values"]',
'Belief leaders inspire through authentic purpose, create meaning for others, and build trust through consistent values.',
'Believers provide moral compass for teams, maintain ethical standards, and bring passion to organizational missions.'),

('Consistency', 'Executing', 'People exceptionally talented in the Consistency theme are keenly aware of the need to treat people the same. They try to treat everyone with equality by setting up clear rules and adhering to them.',
'["Strong sense of fairness", "Desire for equal treatment", "Clear rule establishment", "Predictable decision-making", "Justice-oriented thinking"]',
'["Create clear policies and procedures", "Communicate expectations consistently", "Listen to concerns about fairness", "Apply rules uniformly", "Build transparent systems"]',
'["Responsibility", "Belief", "Discipline"]',
'["Harmony", "Includer", "Restorative"]',
'["May resist necessary exceptions", "Could stifle innovation", "Risk of bureaucratic approach"]',
'Consistency leaders build fair systems, ensure equal opportunities, and create stable, predictable environments.',
'Consistent team members ensure fair treatment, maintain group harmony, and provide stability during change.'),

('Deliberative', 'Executing', 'People exceptionally talented in the Deliberative theme are best described by the serious care they take in making decisions or choices. They anticipate obstacles.',
'["Careful decision-making process", "Risk assessment expertise", "Thoughtful consideration", "Anticipates problems", "Quality over speed"]',
'["Take time for important decisions", "Create decision-making frameworks", "Ask probing questions", "Research thoroughly", "Trust your instincts"]',
'["Analytical", "Responsibility", "Discipline"]',
'["Strategic", "Futuristic", "Input"]',
'["May slow down decision-making", "Could appear overly cautious", "Risk of analysis paralysis"]',
'Deliberative leaders prevent costly mistakes, make well-considered decisions, and provide thoughtful guidance.',
'Deliberative team members ensure quality outcomes, identify potential problems, and bring careful analysis to decisions.'),

('Discipline', 'Executing', 'People exceptionally talented in the Discipline theme enjoy routine and structure. Their world is best described by the order they create.',
'["Loves structure and routine", "Creates organized systems", "Follows through consistently", "Time management excellence", "Predictable work style"]',
'["Establish clear routines", "Create organizing systems", "Set deadlines and timelines", "Break large tasks into steps", "Maintain clean workspace"]',
'["Achiever", "Responsibility", "Consistency"]',
'["Arranger", "Focus", "Analytical"]',
'["May resist spontaneous changes", "Could be inflexible", "Risk of over-structuring"]',
'Discipline leaders create efficient systems, maintain high standards, and provide structure for team success.',
'Disciplined team members ensure consistent execution, maintain organization, and help teams stay on track.'),

('Focus', 'Executing', 'People exceptionally talented in the Focus theme can take a direction, follow through, and make the corrections necessary to stay on track. They prioritize, then act.',
'["Clear goal orientation", "Eliminates distractions effectively", "Strong prioritization skills", "Sustained concentration", "Results-driven approach"]',
'["Set clear priorities daily", "Remove distractions from environment", "Break goals into milestones", "Say no to non-essential tasks", "Review progress regularly"]',
'["Achiever", "Discipline", "Responsibility"]',
'["Strategic", "Maximizer", "Significance"]',
'["May appear single-minded", "Could miss peripheral opportunities", "Risk of tunnel vision"]',
'Focus leaders drive teams toward clear objectives, eliminate distractions, and maintain momentum toward goals.',
'Focused team members keep projects on track, prioritize effectively, and help teams avoid scope creep.'),

('Responsibility', 'Executing', 'People exceptionally talented in the Responsibility theme take psychological ownership of what they say they will do. They are committed to stable values such as honesty and loyalty.',
'["Strong psychological ownership", "Keeps commitments religiously", "Reliable and dependable", "High ethical standards", "Takes initiative to help"]',
'["Make realistic commitments", "Communicate capacity honestly", "Delegate when appropriate", "Set boundaries", "Document agreements clearly"]',
'["Belief", "Consistency", "Discipline"]',
'["Harmony", "Developer", "Empathy"]',
'["May take on too much", "Could feel guilty saying no", "Risk of being taken advantage of"]',
'Responsibility leaders build trust through reliability, create accountable teams, and model ethical behavior.',
'Responsible team members ensure commitments are met, take ownership of outcomes, and provide dependable support.'),

('Restorative', 'Executing', 'People exceptionally talented in the Restorative theme are adept at dealing with problems. They are good at figuring out what is wrong and resolving it.',
'["Problem-solving expertise", "Identifies what is broken", "Enjoys fixing and improving", "Analytical troubleshooting", "Patient with complex issues"]',
'["Seek challenging problems", "Develop troubleshooting skills", "Learn from failure patterns", "Create improvement systems", "Share solutions with others"]',
'["Analytical", "Discipline", "Deliberative"]',
'["Developer", "Individualization", "Empathy"]',
'["May focus too much on problems", "Could appear critical", "Risk of perfectionism"]',
'Restorative leaders turn around failing situations, solve complex problems, and help organizations improve continuously.',
'Restorative team members identify issues early, provide solutions to problems, and help teams overcome obstacles.'),

-- INFLUENCING DOMAIN STRENGTHS
('Activator', 'Influencing', 'People exceptionally talented in the Activator theme can make things happen by turning thoughts into action. They are often impatient.',
'["Bias toward action", "Turns ideas into reality", "Impatient with delays", "Energizes others to act", "Learning by doing approach"]',
'["Start projects quickly", "Set short-term deadlines", "Find action-oriented partners", "Learn through experimentation", "Celebrate quick wins"]',
'["Self-Assurance", "Command", "Competition"]',
'["Strategic", "Ideation", "Futuristic"]',
'["May act without full planning", "Could appear impatient", "Risk of starting too many things"]',
'Activator leaders drive urgency, overcome inertia, and mobilize teams into action quickly and effectively.',
'Activators get projects started, push through delays, and create momentum that energizes entire teams.'),

('Command', 'Influencing', 'People exceptionally talented in the Command theme have presence. They can take control of a situation and make decisions.',
'["Natural presence and authority", "Comfortable making decisions", "Direct communication style", "Takes charge in crises", "Confronts difficult issues"]',
'["Practice listening actively", "Explain reasoning behind decisions", "Seek input before deciding", "Develop emotional awareness", "Use influence responsibly"]',
'["Self-Assurance", "Competition", "Significance"]',
'["Strategic", "Maximizer", "Arranger"]',
'["May appear dominating", "Could intimidate others", "Risk of not listening enough"]',
'Command leaders take charge in crises, make tough decisions, and provide clear direction when others hesitate.',
'Command team members step up in difficult situations, make decisive calls, and help teams move forward confidently.'),

('Communication', 'Influencing', 'People exceptionally talented in the Communication theme generally find it easy to put their thoughts into words. They are good conversationalists and presenters.',
'["Natural storytelling ability", "Engaging presentation skills", "Finds right words easily", "Enjoys public speaking", "Makes complex ideas accessible"]',
'["Practice different speaking formats", "Develop your unique voice", "Use stories to illustrate points", "Adapt style to audience", "Seek speaking opportunities"]',
'["Woo", "Positivity", "Self-Assurance"]',
'["Strategic", "Input", "Learner"]',
'["May talk too much", "Could dominate conversations", "Risk of style over substance"]',
'Communication leaders inspire through words, articulate vision clearly, and build understanding across diverse groups.',
'Communicators help teams understand complex ideas, facilitate discussions, and represent the group effectively.'),

('Competition', 'Influencing', 'People exceptionally talented in the Competition theme measure their progress against the performance of others. They strive to win first place and revel in contests.',
'["Strong drive to win", "Measures against others", "Enjoys competitive environments", "Performance comparison focus", "Thrives under pressure"]',
'["Set competitive goals", "Find worthy opponents", "Track comparative metrics", "Celebrate victories", "Learn from losses"]',
'["Achiever", "Significance", "Self-Assurance"]',
'["Focus", "Maximizer", "Strategic"]',
'["May create unnecessary competition", "Could appear unsporting", "Risk of win-at-all-costs mentality"]',
'Competition leaders drive high performance, create competitive advantage, and motivate teams to excel.',
'Competitive team members raise performance standards, benchmark against the best, and push teams to win.'),

('Maximizer', 'Influencing', 'People exceptionally talented in the Maximizer theme focus on strengths as a way to stimulate personal and group excellence. They seek to transform something strong into something superb.',
'["Focus on strengths", "Pursues excellence", "Seeks to optimize", "Quality improvement mindset", "Invests in what works"]',
'["Identify your top strengths", "Partner with complementary talents", "Invest time in strength development", "Help others find their strengths", "Avoid fixing weaknesses"]',
'["Individualization", "Developer", "Focus"]',
'["Strategic", "Competition", "Significance"]',
'["May ignore necessary weaknesses", "Could appear elitist", "Risk of perfectionism"]',
'Maximizer leaders develop talent, build on strengths, and create conditions for exceptional performance.',
'Maximizers help teammates excel, focus on what works best, and elevate overall team performance.'),

('Self-Assurance', 'Influencing', 'People exceptionally talented in the Self-Assurance theme feel confident in their ability to manage their own lives. They possess an inner compass that gives them confidence that their decisions are right.',
'["Inner confidence", "Independent decision-making", "Trusts own judgment", "Remains calm under pressure", "Takes calculated risks"]',
'["Trust your instincts", "Make decisions confidently", "Take on challenging assignments", "Share your confidence with others", "Learn from mistakes"]',
'["Command", "Competition", "Significance"]',
'["Strategic", "Futuristic", "Activator"]',
'["May appear arrogant", "Could resist feedback", "Risk of overconfidence"]',
'Self-Assured leaders make tough decisions confidently, take risks others avoid, and provide steady leadership.',
'Self-Assured team members bring confidence to difficult situations, make independent decisions, and remain calm under pressure.'),

('Significance', 'Influencing', 'People exceptionally talented in the Significance theme want to make a big impact. They are independent and prioritize projects based on how much influence they will have on their organization or people around them.',
'["Desires to make big impact", "Seeks recognition and visibility", "Independent work style", "Legacy-minded thinking", "Influence-driven decisions"]',
'["Seek high-impact projects", "Build your reputation", "Network with influential people", "Document your achievements", "Mentor others"]',
'["Self-Assurance", "Command", "Competition"]',
'["Strategic", "Futuristic", "Maximizer"]',
'["May seek attention inappropriately", "Could appear self-serving", "Risk of neglecting team needs"]',
'Significance leaders create lasting impact, build organizational reputation, and inspire others to think big.',
'Significant team members drive important initiatives, raise the profile of team work, and help achieve recognition.'),

('Woo', 'Influencing', 'People exceptionally talented in the Woo theme love the challenge of meeting new people and winning them over. They derive satisfaction from breaking the ice and making a connection with someone.',
'["Enjoys meeting new people", "Natural charm and charisma", "Breaks ice easily", "Builds rapport quickly", "Networker mindset"]',
'["Attend networking events", "Practice conversation starters", "Connect people with each other", "Build diverse networks", "Use charm appropriately"]',
'["Communication", "Positivity", "Includer"]',
'["Strategic", "Relator", "Individualization"]',
'["May have surface-level relationships", "Could appear insincere", "Risk of overcommitting socially"]',
'Woo leaders build extensive networks, create buy-in for initiatives, and connect organizations to opportunities.',
'Woo team members expand team networks, build external relationships, and help teams connect with stakeholders.'),

-- RELATIONSHIP BUILDING DOMAIN STRENGTHS
('Adaptability', 'Relationship Building', 'People exceptionally talented in the Adaptability theme prefer to go with the flow. They tend to be now people who take things as they come and discover the future one day at a time.',
'["Goes with the flow", "Flexible and responsive", "Lives in the present", "Handles change well", "Calm under pressure"]',
'["Embrace spontaneous opportunities", "Practice stress management", "Partner with planners", "Stay present-focused", "Learn to communicate changes"]',
'["Positivity", "Includer", "Developer"]',
'["Strategic", "Arranger", "Context"]',
'["May appear unprepared", "Could lack long-term focus", "Risk of being too reactive"]',
'Adaptable leaders navigate change smoothly, help organizations pivot quickly, and maintain calm during uncertainty.',
'Adaptable team members handle unexpected changes, reduce stress during transitions, and keep teams flexible.'),

('Connectedness', 'Relationship Building', 'People exceptionally talented in the Connectedness theme have faith in the links among all things. They believe there are few coincidences and that almost every event has meaning.',
'["Sees connections between things", "Believes in greater purpose", "Considers global implications", "Values spiritual dimension", "Looks for meaning"]',
'["Seek diverse perspectives", "Consider broader implications", "Practice mindfulness", "Build bridges between groups", "Share your insights"]',
'["Belief", "Includer", "Empathy"]',
'["Context", "Input", "Intellection"]',
'["May appear too philosophical", "Could overwhelm with big picture", "Risk of seeming impractical"]',
'Connected leaders build inclusive cultures, consider global impacts, and help organizations find deeper purpose.',
'Connected team members provide perspective on decisions, bridge different groups, and help teams see larger meaning.'),

('Developer', 'Relationship Building', 'People exceptionally talented in the Developer theme recognize and cultivate the potential in others. They spot the signs of each small improvement and derive satisfaction from evidence of progress.',
'["Sees potential in others", "Enjoys helping people grow", "Celebrates incremental progress", "Patient with development", "Invests in people"]',
'["Identify peoples potential", "Provide regular feedback", "Celebrate small wins", "Create learning opportunities", "Be patient with progress"]',
'["Individualization", "Empathy", "Positivity"]',
'["Maximizer", "Strategic", "Learner"]',
'["May over-invest in poor performers", "Could be too patient", "Risk of neglecting high performers"]',
'Developer leaders build talent pipelines, create growth cultures, and help organizations develop capabilities.',
'Developers mentor team members, identify growth opportunities, and help everyone reach their potential.'),

('Empathy', 'Relationship Building', 'People exceptionally talented in the Empathy theme can sense other peoples emotions by imagining themselves in others lives or situations.',
'["Senses others emotions", "Understands different perspectives", "Provides emotional support", "Intuitive about feelings", "Creates safe spaces"]',
'["Listen actively to others", "Validate peoples feelings", "Practice self-care", "Set emotional boundaries", "Use empathy strategically"]',
'["Harmony", "Individualization", "Developer"]',
'["Communication", "Includer", "Positivity"]',
'["May become emotionally drained", "Could take on others problems", "Risk of being manipulated"]',
'Empathetic leaders understand team dynamics, resolve conflicts effectively, and create psychologically safe environments.',
'Empathetic team members provide emotional support, understand unspoken concerns, and help teams work together harmoniously.'),

('Harmony', 'Relationship Building', 'People exceptionally talented in the Harmony theme look for consensus. They dont enjoy conflict; rather, they seek areas of agreement.',
'["Seeks consensus and agreement", "Avoids conflict situations", "Finds common ground", "Diplomatic approach", "Values team unity"]',
'["Practice conflict resolution", "Focus on shared goals", "Learn to address necessary conflicts", "Build on agreements", "Facilitate discussions"]',
'["Empathy", "Includer", "Adaptability"]',
'["Communication", "Woo", "Developer"]',
'["May avoid necessary conflicts", "Could compromise too quickly", "Risk of superficial agreements"]',
'Harmony leaders build consensus, resolve conflicts diplomatically, and create collaborative team environments.',
'Harmony team members reduce friction, find compromise solutions, and help teams work together peacefully.'),

('Includer', 'Relationship Building', 'People exceptionally talented in the Includer theme want to include others. They show awareness of those who feel left out and make an effort to include them.',
'["Includes everyone", "Notices who is left out", "Values diversity", "Creates belonging", "Accepts others readily"]',
'["Actively invite participation", "Notice who is quiet", "Create inclusive practices", "Value different perspectives", "Build diverse teams"]',
'["Empathy", "Harmony", "Connectedness"]',
'["Woo", "Communication", "Developer"]',
'["May include inappropriate people", "Could slow decision-making", "Risk of lowering standards"]',
'Includer leaders build diverse teams, ensure everyone belongs, and create cultures where all voices are heard.',
'Includer team members ensure no one is left out, value all perspectives, and help teams leverage diversity.'),

('Individualization', 'Relationship Building', 'People exceptionally talented in the Individualization theme are intrigued with the unique qualities of each person. They have a gift for figuring out how different people can work together productively.',
'["Sees unique qualities in people", "Customizes approach per person", "Appreciates differences", "Matches people to roles", "Personalizes interactions"]',
'["Study individual differences", "Customize your approach", "Help people find right roles", "Avoid stereotyping", "Celebrate uniqueness"]',
'["Developer", "Empathy", "Maximizer"]',
'["Arranger", "Strategic", "Communication"]',
'["May appear to play favorites", "Could over-customize", "Risk of being inconsistent"]',
'Individualization leaders optimize team composition, leverage unique talents, and help people find their best fit.',
'Individualization team members help match people to tasks, appreciate different working styles, and optimize team effectiveness.'),

('Positivity', 'Relationship Building', 'People exceptionally talented in the Positivity theme have contagious enthusiasm. They are upbeat and can get others excited about what they are going to do.',
'["Contagious enthusiasm", "Optimistic outlook", "Energizes others", "Finds silver linings", "Celebrates successes"]',
'["Share your enthusiasm", "Look for positives in situations", "Celebrate team successes", "Surround yourself with positive people", "Practice gratitude"]',
'["Woo", "Communication", "Developer"]',
'["Strategic", "Maximizer", "Activator"]',
'["May appear unrealistic", "Could ignore real problems", "Risk of toxic positivity"]',
'Positive leaders create energizing environments, boost team morale, and help organizations maintain optimism.',
'Positive team members lift team spirits, celebrate achievements, and help teams maintain motivation during challenges.'),

('Relator', 'Relationship Building', 'People exceptionally talented in the Relator theme enjoy close relationships with others. They find deep satisfaction in working hard with friends to achieve a goal.',
'["Values deep relationships", "Prefers small groups", "Loyal to friends", "Enjoys collaboration", "Builds trust gradually"]',
'["Invest in deeper relationships", "Work with people you trust", "Take time to build connections", "Be vulnerable appropriately", "Value quality over quantity"]',
'["Empathy", "Developer", "Individualization"]',
'["Communication", "Harmony", "Responsibility"]',
'["May have limited network", "Could appear cliquish", "Risk of excluding others"]',
'Relator leaders build loyal teams, create trust-based cultures, and develop deep organizational relationships.',
'Relator team members provide stability, build deep trust, and create strong team bonds that last over time.'),

-- STRATEGIC THINKING DOMAIN STRENGTHS
('Analytical', 'Strategic Thinking', 'People exceptionally talented in the Analytical theme search for reasons and causes. They have the ability to think about all of the factors that might affect a situation.',
'["Seeks reasons and causes", "Logical thinking process", "Data-driven decisions", "Questions assumptions", "Systematic approach"]',
'["Gather comprehensive data", "Ask probing questions", "Test your theories", "Explain your logic", "Partner with action-oriented people"]',
'["Deliberative", "Input", "Intellection"]',
'["Activator", "Command", "Self-Assurance"]',
'["May over-analyze decisions", "Could appear slow", "Risk of analysis paralysis"]',
'Analytical leaders make data-driven decisions, identify root causes, and help organizations think through complex issues.',
'Analytical team members provide logical frameworks, question assumptions, and ensure decisions are well-reasoned.'),

('Context', 'Strategic Thinking', 'People exceptionally talented in the Context theme enjoy thinking about the past. They understand the present by researching its history.',
'["Values historical perspective", "Learns from the past", "Understands patterns", "Provides background context", "Sees how we got here"]',
'["Study relevant history", "Share historical lessons", "Document institutional knowledge", "Connect past to present", "Preserve important traditions"]',
'["Input", "Learner", "Intellection"]',
'["Futuristic", "Strategic", "Ideation"]',
'["May be stuck in the past", "Could resist necessary change", "Risk of over-explaining history"]',
'Context leaders prevent repeated mistakes, preserve valuable traditions, and help organizations learn from experience.',
'Context team members provide historical perspective, preserve institutional knowledge, and help teams understand background.'),

('Futuristic', 'Strategic Thinking', 'People exceptionally talented in the Futuristic theme are inspired by the future and what could be. They energize others with their visions of the future.',
'["Inspired by future possibilities", "Vivid imagination", "Sees potential outcomes", "Energizes with vision", "Long-term perspective"]',
'["Share your visions", "Plan for multiple scenarios", "Connect present to future", "Inspire with possibilities", "Learn forecasting methods"]',
'["Strategic", "Ideation", "Activator"]',
'["Context", "Deliberative", "Analytical"]',
'["May appear unrealistic", "Could ignore present needs", "Risk of impractical dreaming"]',
'Futuristic leaders create compelling visions, anticipate trends, and help organizations prepare for tomorrow.',
'Futuristic team members provide long-term perspective, anticipate changes, and inspire teams with possibilities.'),

('Ideation', 'Strategic Thinking', 'People exceptionally talented in the Ideation theme are fascinated by ideas. They are able to find connections between seemingly disparate phenomena.',
'["Fascinated by ideas", "Creative connections", "Innovative thinking", "Sees patterns others miss", "Generates alternatives"]',
'["Schedule idea generation time", "Capture ideas systematically", "Connect unrelated concepts", "Partner with implementers", "Build on others ideas"]',
'["Strategic", "Input", "Futuristic"]',
'["Activator", "Focus", "Discipline"]',
'["May have too many ideas", "Could appear scattered", "Risk of not following through"]',
'Ideation leaders drive innovation, solve complex problems creatively, and help organizations think differently.',
'Ideation team members generate creative solutions, see new possibilities, and help teams break through mental barriers.'),

('Input', 'Strategic Thinking', 'People exceptionally talented in the Input theme have a craving to know more. Often they like to collect and archive all kinds of information.',
'["Craves knowledge", "Collects information", "Natural curiosity", "Retains facts well", "Resource for others"]',
'["Develop information systems", "Share knowledge with others", "Stay current in your field", "Ask lots of questions", "Connect people to information"]',
'["Learner", "Context", "Intellection"]',
'["Communication", "Strategic", "Maximizer"]',
'["May hoard information", "Could get lost in details", "Risk of information overload"]',
'Input leaders make well-informed decisions, provide comprehensive analysis, and help organizations access needed information.',
'Input team members serve as information resources, provide research support, and help teams stay well-informed.'),

('Intellection', 'Strategic Thinking', 'People exceptionally talented in the Intellection theme are characterized by their intellectual activity. They are introspective and appreciate intellectual discussions.',
'["Enjoys intellectual activity", "Thinks things through", "Introspective nature", "Appreciates mental challenges", "Needs thinking time"]',
'["Schedule regular thinking time", "Find intellectual partners", "Write to clarify thoughts", "Engage in deep discussions", "Research topics thoroughly"]',
'["Input", "Analytical", "Learner"]',
'["Activator", "Communication", "Woo"]',
'["May appear withdrawn", "Could over-think decisions", "Risk of being too theoretical"]',
'Intellection leaders provide thoughtful analysis, solve complex problems, and help organizations think deeply about issues.',
'Intellection team members bring deep thinking, provide thorough analysis, and help teams consider all angles.'),

('Learner', 'Strategic Thinking', 'People exceptionally talented in the Learner theme have a great desire to learn and want to continuously improve. The process of learning, rather than the outcome, excites them.',
'["Great desire to learn", "Enjoys the learning process", "Continuously improving", "Seeks new knowledge", "Growth mindset"]',
'["Take on learning challenges", "Find great teachers", "Practice new skills", "Document learning journey", "Share knowledge with others"]',
'["Input", "Intellection", "Context"]',
'["Developer", "Maximizer", "Individualization"]',
'["May start but not finish", "Could appear restless", "Risk of learning without applying"]',
'Learner leaders stay current with trends, adapt to change, and help organizations build learning cultures.',
'Learner team members bring new knowledge, adapt quickly to changes, and help teams stay current with best practices.'),

('Strategic', 'Strategic Thinking', 'People exceptionally talented in the Strategic theme create alternative ways to proceed. Faced with any given scenario, they can quickly spot the relevant patterns and issues.',
'["Sees patterns and alternatives", "Thinks systematically", "Anticipates obstacles", "Creates multiple options", "Big picture perspective"]',
'["Think through scenarios", "Plan alternative routes", "Ask what if questions", "Simplify complex situations", "Share your strategic insights"]',
'["Futuristic", "Ideation", "Analytical"]',
'["Activator", "Focus", "Command"]',
'["May appear indecisive", "Could over-complicate", "Risk of endless planning"]',
'Strategic leaders anticipate challenges, create comprehensive plans, and help organizations navigate complexity.',
'Strategic team members provide planning expertise, identify potential problems, and help teams think ahead.');

-- =============================================================================
-- MINI-IPIP QUESTION BANK (50 questions covering Big Five personality factors)
-- =============================================================================

INSERT INTO questions (question_text, question_type, theme_mapping, scoring_key, language, difficulty_level, estimated_time_seconds, question_category, reverse_scored) VALUES

-- Extraversion Questions
('I am the life of the party.', 'likert_5', '{"primary": ["Communication", "Woo", "Positivity"], "secondary": ["Command", "Activator"]}', '{"scale": [1,2,3,4,5], "factor": "extraversion", "direction": "positive"}', 'en', 2, 20, 'extraversion', FALSE),
('I feel comfortable around people.', 'likert_5', '{"primary": ["Woo", "Communication", "Relator"], "secondary": ["Empathy", "Includer"]}', '{"scale": [1,2,3,4,5], "factor": "extraversion", "direction": "positive"}', 'en', 2, 20, 'extraversion', FALSE),
('I start conversations.', 'likert_5', '{"primary": ["Communication", "Woo", "Activator"], "secondary": ["Command", "Self-Assurance"]}', '{"scale": [1,2,3,4,5], "factor": "extraversion", "direction": "positive"}', 'en', 2, 25, 'extraversion', FALSE),
('I talk to a lot of different people at parties.', 'likert_5', '{"primary": ["Woo", "Communication", "Includer"], "secondary": ["Positivity", "Relator"]}', '{"scale": [1,2,3,4,5], "factor": "extraversion", "direction": "positive"}', 'en', 2, 25, 'extraversion', FALSE),
('I dont mind being the center of attention.', 'likert_5', '{"primary": ["Significance", "Communication", "Command"], "secondary": ["Self-Assurance", "Woo"]}', '{"scale": [1,2,3,4,5], "factor": "extraversion", "direction": "positive"}', 'en', 3, 25, 'extraversion', FALSE),
('I dont talk a lot.', 'likert_5', '{"primary": ["Intellection", "Deliberative", "Context"], "secondary": ["Analytical", "Input"]}', '{"scale": [5,4,3,2,1], "factor": "extraversion", "direction": "negative"}', 'en', 2, 20, 'extraversion', TRUE),
('I keep in the background.', 'likert_5', '{"primary": ["Harmony", "Adaptability", "Empathy"], "secondary": ["Individualization", "Developer"]}', '{"scale": [5,4,3,2,1], "factor": "extraversion", "direction": "negative"}', 'en', 2, 20, 'extraversion', TRUE),
('I have little to say.', 'likert_5', '{"primary": ["Intellection", "Deliberative", "Input"], "secondary": ["Context", "Analytical"]}', '{"scale": [5,4,3,2,1], "factor": "extraversion", "direction": "negative"}', 'en', 2, 20, 'extraversion', TRUE),
('I would describe my experiences as somewhat dull.', 'likert_5', '{"primary": ["Consistency", "Discipline", "Responsibility"], "secondary": ["Deliberative", "Harmony"]}', '{"scale": [5,4,3,2,1], "factor": "extraversion", "direction": "negative"}', 'en', 3, 30, 'extraversion', TRUE),
('I do not like to draw attention to myself.', 'likert_5', '{"primary": ["Harmony", "Empathy", "Includer"], "secondary": ["Adaptability", "Developer"]}', '{"scale": [5,4,3,2,1], "factor": "extraversion", "direction": "negative"}', 'en', 2, 25, 'extraversion', TRUE),

-- Agreeableness Questions
('I feel others emotions.', 'likert_5', '{"primary": ["Empathy", "Individualization", "Developer"], "secondary": ["Harmony", "Includer"]}', '{"scale": [1,2,3,4,5], "factor": "agreeableness", "direction": "positive"}', 'en', 2, 25, 'agreeableness', FALSE),
('I am concerned about others.', 'likert_5', '{"primary": ["Empathy", "Developer", "Includer"], "secondary": ["Connectedness", "Responsibility"]}', '{"scale": [1,2,3,4,5], "factor": "agreeableness", "direction": "positive"}', 'en', 2, 20, 'agreeableness', FALSE),
('I make people feel at ease.', 'likert_5', '{"primary": ["Harmony", "Empathy", "Positivity"], "secondary": ["Woo", "Includer"]}', '{"scale": [1,2,3,4,5], "factor": "agreeableness", "direction": "positive"}', 'en', 2, 25, 'agreeableness', FALSE),
('I have a soft heart.', 'likert_5', '{"primary": ["Empathy", "Developer", "Harmony"], "secondary": ["Includer", "Connectedness"]}', '{"scale": [1,2,3,4,5], "factor": "agreeableness", "direction": "positive"}', 'en', 2, 20, 'agreeableness', FALSE),
('I take time out for others.', 'likert_5', '{"primary": ["Developer", "Empathy", "Responsibility"], "secondary": ["Includer", "Relator"]}', '{"scale": [1,2,3,4,5], "factor": "agreeableness", "direction": "positive"}', 'en', 2, 25, 'agreeableness', FALSE),
('I am not interested in other peoples problems.', 'likert_5', '{"primary": ["Focus", "Achiever", "Competition"], "secondary": ["Self-Assurance", "Command"]}', '{"scale": [5,4,3,2,1], "factor": "agreeableness", "direction": "negative"}', 'en', 3, 30, 'agreeableness', TRUE),
('I insult people.', 'likert_5', '{"primary": ["Command", "Competition", "Significance"], "secondary": ["Self-Assurance", "Activator"]}', '{"scale": [5,4,3,2,1], "factor": "agreeableness", "direction": "negative"}', 'en', 2, 20, 'agreeableness', TRUE),
('I am not really interested in others.', 'likert_5', '{"primary": ["Focus", "Achiever", "Strategic"], "secondary": ["Discipline", "Analytical"]}', '{"scale": [5,4,3,2,1], "factor": "agreeableness", "direction": "negative"}', 'en', 3, 25, 'agreeableness', TRUE),
('I feel little concern for others.', 'likert_5', '{"primary": ["Focus", "Competition", "Achiever"], "secondary": ["Strategic", "Command"]}', '{"scale": [5,4,3,2,1], "factor": "agreeableness", "direction": "negative"}', 'en', 3, 25, 'agreeableness', TRUE),
('I make people feel uncomfortable.', 'likert_5', '{"primary": ["Command", "Competition", "Self-Assurance"], "secondary": ["Significance", "Analytical"]}', '{"scale": [5,4,3,2,1], "factor": "agreeableness", "direction": "negative"}', 'en', 3, 30, 'agreeableness', TRUE),

-- Conscientiousness Questions
('I am always prepared.', 'likert_5', '{"primary": ["Discipline", "Responsibility", "Deliberative"], "secondary": ["Focus", "Achiever"]}', '{"scale": [1,2,3,4,5], "factor": "conscientiousness", "direction": "positive"}', 'en', 2, 20, 'conscientiousness', FALSE),
('I pay attention to details.', 'likert_5', '{"primary": ["Discipline", "Analytical", "Deliberative"], "secondary": ["Focus", "Input"]}', '{"scale": [1,2,3,4,5], "factor": "conscientiousness", "direction": "positive"}', 'en', 2, 25, 'conscientiousness', FALSE),
('I get chores done right away.', 'likert_5', '{"primary": ["Achiever", "Activator", "Responsibility"], "secondary": ["Discipline", "Focus"]}', '{"scale": [1,2,3,4,5], "factor": "conscientiousness", "direction": "positive"}', 'en', 2, 25, 'conscientiousness', FALSE),
('I like order.', 'likert_5', '{"primary": ["Discipline", "Arranger", "Consistency"], "secondary": ["Focus", "Responsibility"]}', '{"scale": [1,2,3,4,5], "factor": "conscientiousness", "direction": "positive"}', 'en', 1, 20, 'conscientiousness', FALSE),
('I follow a schedule.', 'likert_5', '{"primary": ["Discipline", "Focus", "Responsibility"], "secondary": ["Achiever", "Consistency"]}', '{"scale": [1,2,3,4,5], "factor": "conscientiousness", "direction": "positive"}', 'en', 2, 20, 'conscientiousness', FALSE),
('I mess things up.', 'likert_5', '{"primary": ["Adaptability", "Ideation", "Positivity"], "secondary": ["Activator", "Woo"]}', '{"scale": [5,4,3,2,1], "factor": "conscientiousness", "direction": "negative"}', 'en', 2, 20, 'conscientiousness', TRUE),
('I often forget to put things back in their proper place.', 'likert_5', '{"primary": ["Adaptability", "Ideation", "Futuristic"], "secondary": ["Activator", "Communication"]}', '{"scale": [5,4,3,2,1], "factor": "conscientiousness", "direction": "negative"}', 'en', 3, 35, 'conscientiousness', TRUE),
('I shirk my duties.', 'likert_5', '{"primary": ["Adaptability", "Ideation", "Woo"], "secondary": ["Positivity", "Communication"]}', '{"scale": [5,4,3,2,1], "factor": "conscientiousness", "direction": "negative"}', 'en', 2, 25, 'conscientiousness', TRUE),
('I leave my belongings around.', 'likert_5', '{"primary": ["Adaptability", "Ideation", "Activator"], "secondary": ["Woo", "Positivity"]}', '{"scale": [5,4,3,2,1], "factor": "conscientiousness", "direction": "negative"}', 'en', 2, 25, 'conscientiousness', TRUE),
('I do not like order.', 'likert_5', '{"primary": ["Adaptability", "Ideation", "Activator"], "secondary": ["Communication", "Woo"]}', '{"scale": [5,4,3,2,1], "factor": "conscientiousness", "direction": "negative"}', 'en', 2, 20, 'conscientiousness', TRUE),

-- Neuroticism Questions (Emotional Stability)
('I get stressed out easily.', 'likert_5', '{"primary": ["Empathy", "Harmony", "Adaptability"], "secondary": ["Developer", "Includer"]}', '{"scale": [1,2,3,4,5], "factor": "neuroticism", "direction": "positive"}', 'en', 2, 25, 'neuroticism', FALSE),
('I worry about things.', 'likert_5', '{"primary": ["Deliberative", "Responsibility", "Analytical"], "secondary": ["Input", "Context"]}', '{"scale": [1,2,3,4,5], "factor": "neuroticism", "direction": "positive"}', 'en', 2, 20, 'neuroticism', FALSE),
('I am easily disturbed.', 'likert_5', '{"primary": ["Empathy", "Harmony", "Individualization"], "secondary": ["Adaptability", "Developer"]}', '{"scale": [1,2,3,4,5], "factor": "neuroticism", "direction": "positive"}', 'en', 2, 25, 'neuroticism', FALSE),
('I get upset easily.', 'likert_5', '{"primary": ["Empathy", "Harmony", "Belief"], "secondary": ["Responsibility", "Developer"]}', '{"scale": [1,2,3,4,5], "factor": "neuroticism", "direction": "positive"}', 'en', 2, 20, 'neuroticism', FALSE),
('I change my mood a lot.', 'likert_5', '{"primary": ["Adaptability", "Empathy", "Ideation"], "secondary": ["Individualization", "Harmony"]}', '{"scale": [1,2,3,4,5], "factor": "neuroticism", "direction": "positive"}', 'en', 2, 25, 'neuroticism', FALSE),
('I am relaxed most of the time.', 'likert_5', '{"primary": ["Self-Assurance", "Positivity", "Adaptability"], "secondary": ["Harmony", "Consistency"]}', '{"scale": [5,4,3,2,1], "factor": "neuroticism", "direction": "negative"}', 'en', 2, 25, 'neuroticism', TRUE),
('I seldom feel blue.', 'likert_5', '{"primary": ["Positivity", "Self-Assurance", "Achiever"], "secondary": ["Woo", "Competition"]}', '{"scale": [5,4,3,2,1], "factor": "neuroticism", "direction": "negative"}', 'en', 3, 25, 'neuroticism', TRUE),
('I feel comfortable with myself.', 'likert_5', '{"primary": ["Self-Assurance", "Positivity", "Belief"], "secondary": ["Confidence", "Consistency"]}', '{"scale": [5,4,3,2,1], "factor": "neuroticism", "direction": "negative"}', 'en', 2, 25, 'neuroticism', TRUE),
('I rarely get irritated.', 'likert_5', '{"primary": ["Harmony", "Adaptability", "Positivity"], "secondary": ["Empathy", "Patience"]}', '{"scale": [5,4,3,2,1], "factor": "neuroticism", "direction": "negative"}', 'en', 3, 25, 'neuroticism', TRUE),
('I am not easily bothered by things.', 'likert_5', '{"primary": ["Self-Assurance", "Focus", "Discipline"], "secondary": ["Consistency", "Responsibility"]}', '{"scale": [5,4,3,2,1], "factor": "neuroticism", "direction": "negative"}', 'en', 3, 30, 'neuroticism', TRUE),

-- Openness to Experience Questions
('I have a rich vocabulary.', 'likert_5', '{"primary": ["Communication", "Input", "Learner"], "secondary": ["Intellection", "Context"]}', '{"scale": [1,2,3,4,5], "factor": "openness", "direction": "positive"}', 'en', 2, 25, 'openness', FALSE),
('I have a vivid imagination.', 'likert_5', '{"primary": ["Ideation", "Futuristic", "Strategic"], "secondary": ["Learner", "Input"]}', '{"scale": [1,2,3,4,5], "factor": "openness", "direction": "positive"}', 'en', 2, 25, 'openness', FALSE),
('I have excellent ideas.', 'likert_5', '{"primary": ["Ideation", "Strategic", "Futuristic"], "secondary": ["Intellection", "Learner"]}', '{"scale": [1,2,3,4,5], "factor": "openness", "direction": "positive"}', 'en', 2, 20, 'openness', FALSE),
('I am quick to understand things.', 'likert_5', '{"primary": ["Learner", "Analytical", "Strategic"], "secondary": ["Input", "Intellection"]}', '{"scale": [1,2,3,4,5], "factor": "openness", "direction": "positive"}', 'en', 2, 25, 'openness', FALSE),
('I use difficult words.', 'likert_5', '{"primary": ["Communication", "Significance", "Intellection"], "secondary": ["Input", "Learner"]}', '{"scale": [1,2,3,4,5], "factor": "openness", "direction": "positive"}', 'en', 3, 25, 'openness', FALSE),
('I have difficulty understanding abstract ideas.', 'likert_5', '{"primary": ["Focus", "Achiever", "Responsibility"], "secondary": ["Discipline", "Consistency"]}', '{"scale": [5,4,3,2,1], "factor": "openness", "direction": "negative"}', 'en', 4, 35, 'openness', TRUE),
('I am not interested in abstract ideas.', 'likert_5', '{"primary": ["Focus", "Achiever", "Activator"], "secondary": ["Responsibility", "Competition"]}', '{"scale": [5,4,3,2,1], "factor": "openness", "direction": "negative"}', 'en', 3, 30, 'openness', TRUE),
('I do not have a good imagination.', 'likert_5', '{"primary": ["Focus", "Discipline", "Analytical"], "secondary": ["Responsibility", "Consistency"]}', '{"scale": [5,4,3,2,1], "factor": "openness", "direction": "negative"}', 'en', 3, 30, 'openness', TRUE),
('I have trouble understanding abstract ideas.', 'likert_5', '{"primary": ["Focus", "Achiever", "Responsibility"], "secondary": ["Discipline", "Activator"]}', '{"scale": [5,4,3,2,1], "factor": "openness", "direction": "negative"}', 'en', 4, 35, 'openness', TRUE),
('I do not enjoy thinking about complex problems.', 'likert_5', '{"primary": ["Activator", "Positivity", "Woo"], "secondary": ["Communication", "Includer"]}', '{"scale": [5,4,3,2,1], "factor": "openness", "direction": "negative"}', 'en', 4, 40, 'openness', TRUE);

-- =============================================================================
-- ASSESSMENT CONFIGURATIONS
-- =============================================================================

INSERT INTO assessment_configurations (config_name, assessment_type, question_count, time_limit_minutes, randomize_questions, require_all_questions, scoring_algorithm, result_categories, active) VALUES

('Gallup Full Assessment', 'full_assessment', 50, 60, TRUE, TRUE,
'{"algorithm": "weighted_factor_analysis", "weights": {"extraversion": 0.2, "agreeableness": 0.2, "conscientiousness": 0.2, "neuroticism": 0.2, "openness": 0.2}, "normalization": "z_score", "confidence_interval": 0.95}',
'["top_5_strengths", "strength_themes", "development_areas", "blind_spots", "action_items"]', TRUE),

('Quick Strengths Assessment', 'quick_assessment', 25, 30, TRUE, TRUE,
'{"algorithm": "simplified_scoring", "weights": {"extraversion": 0.25, "agreeableness": 0.25, "conscientiousness": 0.25, "openness": 0.25}, "normalization": "percentile", "confidence_interval": 0.90}',
'["top_3_strengths", "primary_theme", "development_focus"]', TRUE),

('Team Assessment', 'team_assessment', 40, 45, FALSE, TRUE,
'{"algorithm": "team_dynamics_analysis", "focus": ["relationship_building", "executing", "influencing"], "team_metrics": ["collaboration", "leadership", "execution"], "confidence_interval": 0.95}',
'["team_strengths", "team_dynamics", "role_recommendations", "collaboration_opportunities"]', TRUE),

('Leadership Assessment', 'leadership_assessment', 45, 50, TRUE, TRUE,
'{"algorithm": "leadership_focused", "weights": {"influencing": 0.3, "executing": 0.25, "strategic_thinking": 0.25, "relationship_building": 0.2}, "leadership_competencies": ["vision", "execution", "people_development"], "confidence_interval": 0.95}',
'["leadership_strengths", "leadership_style", "development_priorities", "team_impact"]', TRUE);

-- =============================================================================
-- QUESTION SETS - LINKING ASSESSMENTS TO QUESTIONS
-- =============================================================================

-- Full Assessment - All 50 questions
INSERT INTO question_sets (config_id, question_id, sequence_order, weight, required)
SELECT 1, question_id,
       ROW_NUMBER() OVER (ORDER BY question_id),
       1.0,
       TRUE
FROM questions;

-- Quick Assessment - 25 questions (5 per factor)
INSERT INTO question_sets (config_id, question_id, sequence_order, weight, required)
SELECT 2, question_id,
       ROW_NUMBER() OVER (ORDER BY question_category, question_id),
       1.2, -- Higher weight for fewer questions
       TRUE
FROM questions
WHERE question_id IN (
    -- 5 extraversion questions
    1, 2, 3, 6, 7,
    -- 5 agreeableness questions
    11, 12, 13, 16, 17,
    -- 5 conscientiousness questions
    21, 22, 23, 26, 27,
    -- 5 neuroticism questions
    31, 32, 33, 36, 37,
    -- 5 openness questions
    41, 42, 43, 46, 47
);

-- Team Assessment - 40 questions focusing on collaboration
INSERT INTO question_sets (config_id, question_id, sequence_order, weight, required)
SELECT 3, question_id,
       ROW_NUMBER() OVER (ORDER BY
           CASE question_category
               WHEN 'agreeableness' THEN 1
               WHEN 'extraversion' THEN 2
               WHEN 'conscientiousness' THEN 3
               WHEN 'openness' THEN 4
               ELSE 5
           END, question_id),
       CASE question_category
           WHEN 'agreeableness' THEN 1.3  -- Higher weight for team dynamics
           WHEN 'extraversion' THEN 1.2   -- Important for team interaction
           ELSE 1.0
       END,
       TRUE
FROM questions
WHERE question_id NOT IN (30, 35, 40, 45, 50); -- Exclude 10 questions

-- Leadership Assessment - 45 questions focusing on leadership traits
INSERT INTO question_sets (config_id, question_id, sequence_order, weight, required)
SELECT 4, question_id,
       ROW_NUMBER() OVER (ORDER BY question_category, question_id),
       CASE question_category
           WHEN 'extraversion' THEN 1.3     -- Leadership presence
           WHEN 'conscientiousness' THEN 1.2 -- Execution ability
           WHEN 'openness' THEN 1.2         -- Strategic thinking
           ELSE 1.0
       END,
       TRUE
FROM questions
WHERE question_id NOT IN (25, 30, 35, 40, 50); -- Exclude 5 questions

-- =============================================================================
-- SYSTEM CONFIGURATION DATA
-- =============================================================================

-- Insert system metadata
INSERT INTO audit_trails (session_id, action_type, entity_type, entity_id, new_values, timestamp) VALUES
(NULL, 'data_created', 'system', 'seed_data',
 json_object(
     'strengths_count', 34,
     'questions_count', 50,
     'configurations_count', 4,
     'seed_version', '1.0.0',
     'created_by', 'system_initialization'
 ),
 CURRENT_TIMESTAMP);

-- =============================================================================
-- VERIFICATION QUERIES (for testing seed data integrity)
-- =============================================================================

-- Verify all 34 strengths are present
-- SELECT theme, COUNT(*) as strength_count FROM gallup_strengths GROUP BY theme;

-- Verify question distribution
-- SELECT question_category, COUNT(*) as question_count FROM questions GROUP BY question_category;

-- Verify assessment configurations
-- SELECT config_name, question_count, time_limit_minutes FROM assessment_configurations WHERE active = TRUE;

-- Verify question set mappings
-- SELECT ac.config_name, COUNT(qs.question_id) as mapped_questions
-- FROM assessment_configurations ac
-- JOIN question_sets qs ON ac.config_id = qs.config_id
-- GROUP BY ac.config_name;

-- =============================================================================
-- DATA INTEGRITY NOTES
-- =============================================================================
-- 1. All 34 Gallup strengths included with complete metadata
-- 2. 50 Mini-IPIP questions covering Big Five personality factors
-- 3. JSON-based theme mappings link personality traits to strengths
-- 4. Multiple assessment configurations for different use cases
-- 5. Question sets properly weighted for different assessment types
-- 6. All reference data includes comprehensive descriptions and guidance
-- 7. Scoring algorithms configured for different assessment contexts
-- 8. System audit trail created for seed data installation
-- =============================================================================