
import React, { useState, useCallback } from 'react';
import { ImageUploader } from './components/ImageUploader';
import { Spinner } from './components/Spinner';
import { Header } from './components/Header';
import { ResultDisplay } from './components/ResultDisplay';
import { generateImageFromPose } from './services/geminiService';
import type { ImageFile } from './types';

type AspectRatio = '1:1' | '9:16' | '16:9';

const App: React.FC = () => {
    const [subjectImage, setSubjectImage] = useState<ImageFile | null>(null);
    const [poseImage, setPoseImage] = useState<ImageFile | null>(null);
    const [generatedImage, setGeneratedImage] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const [aspectRatio, setAspectRatio] = useState<AspectRatio>('1:1');

    const handleImageChange = (
        event: React.ChangeEvent<HTMLInputElement>,
        imageType: 'subject' | 'pose'
    ) => {
        if (event.target.files && event.target.files[0]) {
            const file = event.target.files[0];
            const setter = imageType === 'subject' ? setSubjectImage : setPoseImage;
            setter({
                file: file,
                previewUrl: URL.createObjectURL(file),
            });
            setGeneratedImage(null);
            setError(null);
        }
    };

    const fileToBase64 = (file: File): Promise<string> => {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload = () => {
                const result = reader.result as string;
                resolve(result.split(',')[1]); // Remove the data URL prefix
            };
            reader.onerror = (error) => reject(error);
        });
    };

    const handleGenerate = useCallback(async () => {
        if (!subjectImage || !poseImage) {
            setError("Please upload both a subject and a pose image.");
            return;
        }

        setIsLoading(true);
        setError(null);
        setGeneratedImage(null);

        try {
            const subjectBase64 = await fileToBase64(subjectImage.file);
            const poseBase64 = await fileToBase64(poseImage.file);

            const resultBase64 = await generateImageFromPose(
                subjectBase64,
                subjectImage.file.type,
                poseBase64,
                poseImage.file.type,
                aspectRatio
            );

            if (resultBase64) {
                const newImage = `data:image/png;base64,${resultBase64}`;
                setGeneratedImage(newImage);
            } else {
                setError("The AI could not generate an image from the provided inputs. Please try different images.");
            }
        } catch (err) {
            console.error(err);
            setError(err instanceof Error ? err.message : "An unknown error occurred during image generation.");
        } finally {
            setIsLoading(false);
        }
    }, [subjectImage, poseImage, aspectRatio]);
    
    const canGenerate = subjectImage !== null && poseImage !== null && !isLoading;

    const buttonBaseClasses = "px-6 py-2 text-md font-semibold rounded-full transition-all duration-300 ease-in-out transform hover:scale-105 focus:outline-none focus:ring-4 focus:ring-offset-2 focus:ring-offset-gray-900";
    const primaryButtonClasses = `bg-gradient-to-r from-purple-500 to-indigo-600 hover:from-purple-600 hover:to-indigo-700 shadow-lg`;
    const secondaryButtonClasses = `bg-gray-700 hover:bg-gray-600`;

    return (
        <div className="min-h-screen bg-gray-900 text-white font-sans flex flex-col">
            <Header />
            <main className="flex-grow container mx-auto px-4 py-8">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
                    <ImageUploader
                        id="subject"
                        title="Subject Image"
                        description="Upload a clear photo of the person."
                        imageUrl={subjectImage?.previewUrl}
                        onImageChange={(e) => handleImageChange(e, 'subject')}
                    />
                    <ImageUploader
                        id="pose"
                        title="Pose Reference"
                        description="Upload a photo with the desired pose."
                        imageUrl={poseImage?.previewUrl}
                        onImageChange={(e) => handleImageChange(e, 'pose')}
                    />
                </div>
                
                <div className="text-center mb-8">
                    <div className="flex justify-center gap-4 mb-6">
                        {(['1:1', '9:16', '16:9'] as const).map((ratio) => (
                            <button
                                key={ratio}
                                onClick={() => setAspectRatio(ratio)}
                                className={`${buttonBaseClasses} px-4 py-2 text-sm ${
                                    aspectRatio === ratio
                                        ? primaryButtonClasses
                                        : secondaryButtonClasses
                                }`}
                                aria-label={`Set aspect ratio to ${ratio}`}
                            >
                                {ratio}
                            </button>
                        ))}
                    </div>

                    <button
                        onClick={handleGenerate}
                        disabled={!canGenerate}
                        className={`${buttonBaseClasses} px-8 py-3 text-lg ${canGenerate 
                                ? primaryButtonClasses 
                                : 'bg-gray-600 cursor-not-allowed text-gray-400'
                            }`}
                    >
                        {isLoading ? 'Generating...' : 'Generate Image'}
                    </button>
                </div>

                <div className="w-full max-w-2xl mx-auto p-4 bg-gray-800/50 rounded-2xl shadow-2xl border border-gray-700">
                    <h2 className="text-2xl font-bold text-center text-gray-200 mb-4">Result</h2>
                    {isLoading && <Spinner />}
                    {error && <p className="text-center text-red-400 bg-red-900/50 p-3 rounded-lg">{error}</p>}
                    {!isLoading && <ResultDisplay generatedImage={generatedImage} />}
                </div>
            </main>
            <footer className="text-center py-4 text-gray-500 text-sm">
                <p>Powered by Gemini AI</p>
            </footer>
        </div>
    );
};

export default App;
