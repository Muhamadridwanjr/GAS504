import React from 'react';

class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true, error };
    }

    componentDidCatch(error, errorInfo) {
        console.error("ErrorBoundary caught an error", error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return (
                <div className="min-h-screen bg-[#0a0b0f] flex items-center justify-center p-6 text-center">
                    <div className="max-w-md w-full p-8 bg-[#0d0e12] border border-red-500/30 rounded-2xl shadow-2xl">
                        <div className="w-16 h-16 bg-red-500/10 rounded-full flex items-center justify-center mx-auto mb-6">
                            <span className="text-3xl text-red-500">⚠</span>
                        </div>
                        <h1 className="text-xl font-black text-white mb-2 uppercase tracking-tight">UI Error Detected</h1>
                        <p className="text-[#666] text-sm mb-6 leading-relaxed">
                            Terjadi kesalahan saat merender antarmuka. Kami telah menangkap error ini untuk mencegah crash sistem total.
                        </p>
                        <div className="bg-black/40 rounded-lg p-3 mb-6 text-left overflow-hidden border border-[#1c1d24]">
                            <code className="text-red-400 text-[10px] break-all">
                                {this.state.error?.toString()}
                            </code>
                        </div>
                        <button
                            onClick={() => window.location.reload()}
                            className="w-full py-3 bg-yellow-400 text-black font-black rounded-lg hover:bg-yellow-300 transition-all uppercase text-xs tracking-widest"
                        >
                            Refresh Terminal
                        </button>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}

export default ErrorBoundary;
