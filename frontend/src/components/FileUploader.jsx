import React, { useState } from 'react';
import { Upload, FileText, CheckCircle2, Loader2 } from 'lucide-react';
import axios from 'axios';

const FileUploader = () => {
    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState('');

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
        setMessage('');
    };

    const handleUpload = async () => {
        if (!file) return;
        setLoading(true);
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await axios.post('http://localhost:5000/api/upload', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            setMessage(response.data.message);
            setFile(null);
        } catch (error) {
            setMessage('Error uploading file.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="glass-card max-w-2xl mx-auto mt-20">
            <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                <Upload className="w-6 h-6 text-blue-500" />
                Upload Study Materials
            </h2>

            <div className="border-2 border-dashed border-slate-700 rounded-2xl p-10 flex flex-col items-center justify-center gap-4 bg-slate-900/30">
                <FileText className="w-12 h-12 text-slate-500" />
                <div className="text-center">
                    <p className="text-lg font-medium">Select a PDF or Text file</p>
                    <p className="text-sm text-slate-400">MindGap AI will analyze the content to create lessons for you.</p>
                </div>

                <input
                    type="file"
                    onChange={handleFileChange}
                    className="hidden"
                    id="file-upload"
                    accept=".pdf,.txt"
                />
                <label
                    htmlFor="file-upload"
                    className="btn-secondary cursor-pointer"
                >
                    Choose File
                </label>

                {file && <p className="text-blue-400 font-medium">{file.name}</p>}
            </div>

            <button
                onClick={handleUpload}
                disabled={!file || loading}
                className="w-full mt-6 btn-primary flex items-center justify-center gap-2"
            >
                {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Upload & Process'}
            </button>

            {message && (
                <div className="mt-4 p-4 rounded-xl bg-green-500/10 border border-green-500/20 text-green-400 flex items-center gap-2">
                    <CheckCircle2 className="w-5 h-5" />
                    {message}
                </div>
            )}
        </div>
    );
};

export default FileUploader;
