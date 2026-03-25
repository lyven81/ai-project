"""
Single story — Cinderella.
6 pages x 3 pre-coded options each = 18 story texts and image prompts.
Text is fixed (no AI text generation). Only the illustration is AI-generated.
Every page-N option connects seamlessly to every page-(N+1) option.
"""

STORY = {
    "id": "cinderella",
    "title": "Cinderella",
    "subtitle": "Six pages. Three paths each. Your story.",
    "total_pages": 6,
    "cover_prompt": (
        "Children's coloring book cover illustration. "
        "Cinderella stands at the top of a grand castle staircase in a flowing gown, "
        "looking out at a starlit kingdom below. "
        "Bold thick black outlines, large white fill areas ready to colour. "
        "Fairy-tale castle architecture, tall arched windows, stars and a full moon outside. "
        "Leave space at the top for a title. Warm and inviting, no shading, no colour fill, "
        "professional coloring book illustration for children ages 5-10."
    ),
    "pages": [
        {
            "page": 1,
            "chapter_title": "The Morning Before the Ball",
            "options": [
                {
                    "id": "a",
                    "preview": "Cinderella hums while sweeping, holding onto a quiet hope",
                    "story_text": (
                        "Cinderella hummed softly as she swept the cold stone floors, "
                        "her voice as gentle as spring rain. "
                        "Deep in her heart a quiet hope flickered — "
                        "not for a gown or a dance, but simply to be seen for who she truly was."
                    ),
                    "image_prompt": (
                        "Children's coloring book page. Cinderella sweeping stone castle floors "
                        "with a long broom, wearing a simple dress and apron, "
                        "looking upward with a gentle hopeful smile. "
                        "Sunlight streams through a tall arched window. "
                        "Small birds perch cheerfully on the sill. "
                        "Bold thick black outlines, white fill, no shading, fairy-tale style."
                    ),
                },
                {
                    "id": "b",
                    "preview": "She finds a note in her mother's handwriting tucked inside a book",
                    "story_text": (
                        "Tucked inside an old storybook, Cinderella found a small folded note "
                        "in her mother's handwriting. "
                        "It read: Kindness is the only magic that lasts. "
                        "She pressed it to her heart, suddenly feeling less alone in the world."
                    ),
                    "image_prompt": (
                        "Children's coloring book page. Cinderella sitting by a sunlit window, "
                        "holding a small folded note with a tender, wondering expression. "
                        "An open storybook rests on the table beside her. Dust motes float in warm light. "
                        "Bold thick black outlines, white fill, no shading, fairy-tale style."
                    ),
                },
                {
                    "id": "c",
                    "preview": "A tiny mouse bows to her — her first true friend in this house",
                    "story_text": (
                        "A tiny mouse with bright eyes scurried up and bowed with great formality. "
                        "Cinderella laughed — the first real laugh in months. "
                        "'Well,' she whispered, 'at least I have one friend in this house.' "
                        "The mouse twirled once, as if to say: and a very good one at that."
                    ),
                    "image_prompt": (
                        "Children's coloring book page. Cinderella kneeling on the kitchen floor, "
                        "eye-level with a small friendly mouse that is bowing comically. "
                        "She laughs with pure delight. "
                        "Flour barrels and a stone hearth fill the cozy background. "
                        "Bold thick black outlines, white fill, no shading, fairy-tale style."
                    ),
                },
            ],
        },
        {
            "page": 2,
            "chapter_title": "The Invitation Arrives",
            "options": [
                {
                    "id": "a",
                    "preview": "A royal messenger arrives — the stepmother reads it first",
                    "story_text": (
                        "A royal messenger rode up to the gate, his trumpet gleaming in the sun. "
                        "The stepmother snatched the scroll and read it twice. "
                        "Then she smiled — but it was not the kind of smile "
                        "that meant anything good for Cinderella."
                    ),
                    "image_prompt": (
                        "Children's coloring book page. A royal messenger in a decorated uniform "
                        "presenting a golden scroll at a grand house gate. "
                        "A stern stepmother reaches for it while two stepsisters crowd eagerly behind her. "
                        "Cinderella watches quietly from an upstairs window. "
                        "Bold thick black outlines, white fill, no shading, fairy-tale style."
                    ),
                },
                {
                    "id": "b",
                    "preview": "A stepsister looks at Cinderella with something almost like guilt",
                    "story_text": (
                        "Anastasia, the younger stepsister, grabbed the invitation first. "
                        "For one brief moment she looked at Cinderella with something like guilt — "
                        "almost like an apology. "
                        "Then the stepmother appeared and the moment vanished like smoke."
                    ),
                    "image_prompt": (
                        "Children's coloring book page. A young stepsister holding a fancy invitation scroll, "
                        "glancing back at Cinderella with a complicated, guilty expression. "
                        "Cinderella stands in a doorway, surprised and hopeful. "
                        "A grand foyer with chandelier in the background. "
                        "Bold thick black outlines, white fill, no shading, fairy-tale style."
                    ),
                },
                {
                    "id": "c",
                    "preview": "The invitation blows to Cinderella's feet — it says 'all maidens'",
                    "story_text": (
                        "A gust of wind sent the invitation skidding across the floor "
                        "and it landed right at Cinderella's feet. "
                        "She picked it up and read: All maidens of the kingdom are invited. "
                        "All. The word sat in her chest like a warm ember that refused to go out."
                    ),
                    "image_prompt": (
                        "Children's coloring book page. A royal invitation scroll settling on a stone floor, "
                        "Cinderella bending to pick it up with wide hopeful eyes. "
                        "Wind stirs a curtain at an open window. A warm fireplace glows nearby. "
                        "Bold thick black outlines, white fill, no shading, fairy-tale style."
                    ),
                },
            ],
        },
        {
            "page": 3,
            "chapter_title": "Getting Ready",
            "options": [
                {
                    "id": "a",
                    "preview": "By candlelight she sews herself a gown from fabric scraps",
                    "story_text": (
                        "Cinderella stood before a pile of old fabric scraps. "
                        "She had nimble fingers and a steady eye for beauty. "
                        "By candlelight she began to sew — stitch by careful stitch — "
                        "turning forgotten scraps into something that was entirely her own."
                    ),
                    "image_prompt": (
                        "Children's coloring book page. Cinderella sitting at a small table by a single candle, "
                        "sewing a gown from colourful fabric scraps with focused happy concentration. "
                        "Thread, scissors, and pins arranged nearby. Cozy attic room. "
                        "Bold thick black outlines, white fill, no shading, fairy-tale style."
                    ),
                },
                {
                    "id": "b",
                    "preview": "A mysterious old woman at the gate makes her a quiet promise",
                    "story_text": (
                        "Just as the last carriage rolled away, a shimmer appeared at the garden gate. "
                        "An old woman with very kind eyes stepped forward and said quietly, "
                        "'You shall go — but it begins with you deciding that you deserve to.' "
                        "Cinderella straightened her back and nodded."
                    ),
                    "image_prompt": (
                        "Children's coloring book page. A kindly old woman with a warm glowing aura "
                        "standing at a garden gate, speaking gently to Cinderella. "
                        "Fireflies and stars surround them. Garden flowers frame the scene beautifully. "
                        "Bold thick black outlines, white fill, no shading, fairy-tale style."
                    ),
                },
                {
                    "id": "c",
                    "preview": "Her mouse friend leads her to something glittering hidden by the old oak tree",
                    "story_text": (
                        "The little mouse whistled from behind the flour barrel. "
                        "Cinderella followed him out to the old oak tree, "
                        "where something glittered between the roots — "
                        "a small cloth pouch with a note: Wear what makes you feel like yourself."
                    ),
                    "image_prompt": (
                        "Children's coloring book page. Cinderella kneeling at the mossy roots "
                        "of a large old oak tree at twilight, a small mouse pointing excitedly "
                        "to a glittering cloth pouch tucked between the roots. "
                        "Stars and fireflies in the night garden. "
                        "Bold thick black outlines, white fill, no shading, fairy-tale style."
                    ),
                },
            ],
        },
        {
            "page": 4,
            "chapter_title": "The Grand Ballroom",
            "options": [
                {
                    "id": "a",
                    "preview": "She steps inside, breathes, and lets herself belong — just for tonight",
                    "story_text": (
                        "Cinderella stepped into the hall where golden light fell like rain "
                        "and music threaded through every corner of the air. "
                        "She did not rush toward the dancing. "
                        "She paused, breathed, and decided — just for tonight — to let herself belong here."
                    ),
                    "image_prompt": (
                        "Children's coloring book page. Cinderella standing at the entrance of a grand ballroom, "
                        "looking in with calm wonder and a quiet smile. "
                        "Sparkling chandeliers, swirling couples dancing, tall arched windows behind them. "
                        "She is composed and serene, not overwhelmed. "
                        "Bold thick black outlines, white fill, no shading, fairy-tale style."
                    ),
                },
                {
                    "id": "b",
                    "preview": "The Prince notices her laugh from across the crowded room",
                    "story_text": (
                        "The Prince stood surrounded by admirers but his gaze kept drifting. "
                        "Then Cinderella laughed at something small and entirely private, "
                        "and his attention locked on her — steady as a compass needle finding north. "
                        "He began to make his way across the room."
                    ),
                    "image_prompt": (
                        "Children's coloring book page. A prince in a ballroom standing still "
                        "amid swirling dancers, his gaze fixed on Cinderella across the room "
                        "who is laughing warmly at something. A crowd of guests between them. "
                        "Chandeliers and grand pillars in the background. "
                        "Bold thick black outlines, white fill, no shading, fairy-tale style."
                    ),
                },
                {
                    "id": "c",
                    "preview": "A quiet boy sits beside her by the window — 'Me too. I hate crowds.'",
                    "story_text": (
                        "She found a quiet corner near the tall windows, watching the dancers twirl. "
                        "Then a boy her age sat down beside her and said simply, "
                        "'Me too. I hate crowds.' "
                        "Cinderella looked at him — not a prince, not a courtier — "
                        "just someone who understood exactly how she felt."
                    ),
                    "image_prompt": (
                        "Children's coloring book page. Cinderella sitting on a window ledge "
                        "in a grand ballroom, a friendly young man sitting comfortably beside her, "
                        "both watching the dancing from the peaceful sidelines. "
                        "Moonlight streams through tall windows. Dancing guests in the lively background. "
                        "Bold thick black outlines, white fill, no shading, fairy-tale style."
                    ),
                },
            ],
        },
        {
            "page": 5,
            "chapter_title": "Something Changes",
            "options": [
                {
                    "id": "a",
                    "preview": "The clock strikes midnight — she realises she has not changed at all",
                    "story_text": (
                        "Somewhere in the palace a clock began to strike. "
                        "Twelve deep hollow beats rang through the halls. "
                        "Cinderella froze — not from magic, but from a sudden clarity: "
                        "she was still herself. Gown or no gown, nothing that truly mattered had changed."
                    ),
                    "image_prompt": (
                        "Children's coloring book page. Cinderella standing in a palace corridor, "
                        "a grand ornate clock on the wall with its hands pointing to midnight. "
                        "She looks at the clock with calm realisation rather than fear or panic. "
                        "Soft moonlight from a nearby window. "
                        "Bold thick black outlines, white fill, no shading, fairy-tale style."
                    ),
                },
                {
                    "id": "b",
                    "preview": "The Prince reaches for her hand — 'I don't even know your name'",
                    "story_text": (
                        "The Prince reached for her hand just as the midnight chime rang out. "
                        "'I don't even know your name,' he said quietly. "
                        "She looked him in the eye and smiled. "
                        "Some things, she had decided, are worth saying out loud."
                    ),
                    "image_prompt": (
                        "Children's coloring book page. A prince gently reaching for Cinderella's hand "
                        "on a moonlit palace balcony, the two of them facing each other with warmth. "
                        "Stars and a full moon visible behind them. "
                        "An ornate clock visible through glass balcony doors. "
                        "Bold thick black outlines, white fill, no shading, fairy-tale style."
                    ),
                },
                {
                    "id": "c",
                    "preview": "Instead of running she sits on the steps — then walks back through the door",
                    "story_text": (
                        "Instead of running, Cinderella sat down on the wide marble steps. "
                        "One shoe had slipped off. "
                        "She looked at it for a long quiet moment — then stood up "
                        "and walked back through the glowing door."
                    ),
                    "image_prompt": (
                        "Children's coloring book page. Cinderella sitting on wide marble palace steps at night, "
                        "one glass slipper on her foot and the other lying beside her on the step, "
                        "looking back at the warm glowing palace entrance with a calm determined expression. "
                        "Stars overhead. "
                        "Bold thick black outlines, white fill, no shading, fairy-tale style."
                    ),
                },
            ],
        },
        {
            "page": 6,
            "chapter_title": "The Morning After",
            "options": [
                {
                    "id": "a",
                    "preview": "A horseman comes to every door — she steps forward with calm",
                    "story_text": (
                        "In the quiet of the morning a royal horseman came to each door in the kingdom. "
                        "When he reached Cinderella's house she stepped forward — "
                        "not with trembling, but with calm. "
                        "Some things, once started, simply know how to finish themselves."
                    ),
                    "image_prompt": (
                        "Children's coloring book page. A royal horseman at the front door of a house "
                        "in golden morning light, Cinderella stepping forward with quiet confidence "
                        "past the surprised stepmother and stepsisters. "
                        "A white horse stands proudly in the background. "
                        "Bold thick black outlines, white fill, no shading, fairy-tale style."
                    ),
                },
                {
                    "id": "b",
                    "preview": "She ignores the slipper — and places her mother's note on the table instead",
                    "story_text": (
                        "The glass slipper sat gleaming on a velvet cushion. "
                        "When Cinderella's turn came she did not reach for the slipper. "
                        "Instead she reached into her pocket and placed a small folded note on the table. "
                        "The Prince read it. He looked up. He understood completely."
                    ),
                    "image_prompt": (
                        "Children's coloring book page. Cinderella standing before a prince "
                        "who holds a glass slipper on a velvet cushion, "
                        "but she is calmly placing a small folded note on the table between them. "
                        "The prince reads it with a gentle understanding expression. "
                        "Stepmother and stepsisters watching in bewildered confusion. "
                        "Bold thick black outlines, white fill, no shading, fairy-tale style."
                    ),
                },
                {
                    "id": "c",
                    "preview": "He comes not with a slipper but with a question — and she answers",
                    "story_text": (
                        "The Prince did not come with a slipper. He came with a question: "
                        "'The girl by the window — the one who laughed and then stayed. "
                        "Do you know her?' "
                        "Cinderella looked at her stepsisters. Then she looked at him. "
                        "'Yes,' she said. 'I do.'"
                    ),
                    "image_prompt": (
                        "Children's coloring book page. A prince standing earnestly at the doorway "
                        "of a house in morning light, speaking to Cinderella who stands in the front hall "
                        "with a quiet confident smile. "
                        "The confused stepsisters and stepmother stand behind her. "
                        "Warm sunlight pours through the open door. "
                        "Bold thick black outlines, white fill, no shading, fairy-tale style."
                    ),
                },
            ],
        },
    ],
}
