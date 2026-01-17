import React, { useState, useEffect } from 'react';
import { Mic, MicOff, Loader2, X, Search } from 'lucide-react';
import api from '../services/api';

/**
 * Functional Voice Recorder for various UI contexts
 * @param {string} variant - 'icon' (small button), 'search' (wide bar), 'default' (modal style)
 * @param {function} onResult - callback with parsed data
 */
const VoiceRecorder = ({ onResult, variant = 'default', placeholder = 'Tap to speak...' }) => {
    const [isListening, setIsListening] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);
    const [error, setError] = useState(null);
    const [lastTranscript, setLastTranscript] = useState('');

    // Browser API setup
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = SpeechRecognition ? new SpeechRecognition() : null;

    if (recognition) {
        recognition.continuous = false;
        recognition.interimResults = false; // We only care about final for simple shortcuts
        recognition.lang = 'ar-TN';
    }

    const toggleListening = () => {
        if (!recognition) {
            setError('Browser not supported');
            return;
        }

        if (isListening) {
            recognition.stop();
        } else {
            setError(null);
            setIsListening(true);
            try {
                recognition.start();
            } catch (err) {
                setIsListening(false);
            }
        }
    };

    useEffect(() => {
        if (!recognition) return;

        recognition.onresult = async (event) => {
            const transcript = event.results[0][0].transcript;
            console.log('🎤 Raw Browser Transcript:', transcript);
            setLastTranscript(transcript);
            setIsListening(false);
            handleProcess(transcript);
        };

        recognition.onerror = (event) => {
            setIsListening(false);
            setError(`Error: ${event.error}`);
        };

        recognition.onend = () => setIsListening(false);
    }, [recognition]);

    const handleProcess = async (text) => {
        // 1. Try Local Extraction First (Fastest)
        const digits = text.match(/\d+(\.\d+)?/g);
        if (digits && digits.length > 0) {
            console.log('⚡ Local Digit Found:', digits[0]);
            if (onResult) {
                onResult({ numbers: [parseFloat(digits[0])], raw_text: text }, text);
                setIsProcessing(false);
                return;
            }
        }

        // 2. Fallback to Backend for Derja/French Words
        setIsProcessing(true);
        try {
            const response = await api.parseVoice(text);
            console.log('📡 Backend Parse Result:', response);
            if (onResult) onResult(response, text);
        } catch (err) {
            setError('Retry speaking');
        } finally {
            setIsProcessing(false);
        }
    };

    if (variant === 'icon') {
        return (
            <div className="relative inline-block">
                <button
                    type="button"
                    onClick={toggleListening}
                    className={`p-2 rounded-lg transition-all ${isListening
                        ? 'bg-red-500 text-white animate-pulse'
                        : isProcessing
                            ? 'bg-slate-100 text-slate-400 cursor-wait'
                            : 'bg-emerald-50 text-emerald-600 hover:bg-emerald-100'
                        }`}
                    title="Speak number"
                >
                    {isProcessing ? <Loader2 className="animate-spin" size={16} /> : <Mic size={16} />}
                </button>
                {lastTranscript && !isListening && (
                    <div className="absolute top-full left-1/2 -translate-x-1/2 mt-1 px-3 py-1 bg-slate-900 text-white text-[10px] font-black rounded-lg whitespace-nowrap z-[100] shadow-xl border border-white/20 animate-in fade-in zoom-in duration-300">
                        <span className="text-emerald-400">Heard:</span> "{lastTranscript}"
                    </div>
                )}
            </div>
        );
    }

    if (variant === 'search') {
        return (
            <div className="relative group w-full max-w-md">
                <div className={`flex items-center gap-3 px-6 py-4 bg-white rounded-2xl border-2 transition-all ${isListening ? 'border-red-500 shadow-lg shadow-red-50' : 'border-slate-100 focus-within:border-emerald-500'
                    }`}>
                    <Search className="text-slate-400" size={20} />
                    <div className="flex-1">
                        <p className={`text-sm font-bold ${isListening ? 'text-red-500' : 'text-slate-500'}`}>
                            {isListening ? 'Listening for crop...' : isProcessing ? 'Searching...' : lastTranscript || 'Voice Crop Search'}
                        </p>
                        <p className="text-[10px] text-slate-400 uppercase tracking-widest font-black">
                            Try: "Zitoun", "Batata", "9am7"
                        </p>
                    </div>
                    <button
                        onClick={toggleListening}
                        className={`p-3 rounded-xl transition-all ${isListening ? 'bg-red-500 text-white' : 'bg-slate-900 text-white hover:bg-emerald-600'
                            }`}
                    >
                        {isProcessing ? <Loader2 className="animate-spin" size={20} /> : <Mic size={20} />}
                    </button>
                </div>
                {error && <p className="absolute -bottom-6 left-6 text-[10px] text-red-500 font-bold">{error}</p>}
                {lastTranscript && !isListening && !isProcessing && (
                    <div className="absolute -bottom-6 right-6 text-[10px] text-emerald-600 font-black uppercase tracking-widest">
                        Heard: "{lastTranscript}"
                    </div>
                )}
            </div>
        );
    }

    // Default Modal-ish style for other contexts
    return (
        <div className="flex flex-col items-center gap-4 p-6 bg-slate-50 rounded-3xl border-2 border-dashed border-slate-200">
            <button
                onClick={toggleListening}
                disabled={isProcessing}
                className={`p-6 rounded-full transition-all shadow-lg ${isListening ? 'bg-red-500 text-white' : 'bg-emerald-600 text-white hover:bg-emerald-500'
                    }`}
            >
                {isProcessing ? <Loader2 className="animate-spin" size={32} /> : <Mic size={32} />}
            </button>
            <div className="text-center">
                <p className="font-bold text-slate-700">
                    {isListening ? 'Speak now' : isProcessing ? 'Understanding...' : placeholder}
                </p>
                {lastTranscript && !isListening && (
                    <p className="text-xs text-slate-400 italic mt-1">
                        "{lastTranscript}"
                    </p>
                )}
            </div>
            {error && <p className="text-xs text-red-500 font-medium">{error}</p>}
        </div>
    );
};

export default VoiceRecorder;
