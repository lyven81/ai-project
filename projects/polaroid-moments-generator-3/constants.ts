export interface PosePrompt {
    title: string;
    prompt: string;
}

export const POSE_PROMPTS: PosePrompt[] = [
    {
        title: "Victory Shout",
        prompt: "Three friends stand side by side, fists clenched and faces lit with excitement as if they’ve just won a big game or achieved something together. Their wide smiles and triumphant poses capture a burst of energy and celebration, telling the story of a shared victory moment."
    },
    {
        title: "Whispering a Secret",
        prompt: "Two friends lean in as if one is whispering a secret to the other, while the third friend looks at the camera with a curious or amused expression. This tells a fun little story within the photo."
    },
    {
        title: "Celebration Pose",
        prompt: "Three friends stand close together with arms around each other’s shoulders, grinning widely at the camera. One of them points playfully towards the middle friend, as if highlighting him, while all three radiate energy and joy. This captures the mood of excitement and camaraderie, like they’re celebrating a shared victory or just enjoying the moment together."
    },
    {
        title: "Mixed Reactions",
        prompt: "Three friends strike contrasting poses — one scratches his head with a puzzled look, the middle stands confidently with arms crossed, while the third gestures to himself in surprise. Together, they create a playful scene that feels like a moment of disagreement or misunderstanding, with each showing a different reaction to the same situation."
    }
];