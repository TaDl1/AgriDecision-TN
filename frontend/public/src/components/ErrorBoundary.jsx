/**
 * Error boundary component for catching React errors
 */
import React from 'react';
import { AlertTriangle } from 'lucide-react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  handleReload = () => {
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-red-50 to-orange-50 p-4">
          <div className="max-w-md w-full bg-white rounded-2xl shadow-2xl p-8 text-center animate-scale-in">
            <div className="flex justify-center mb-4">
              <div className="p-4 bg-red-100 rounded-full animate-bounce">
                <AlertTriangle className="text-red-600" size={48} />
              </div>
            </div>

            <h1 className="text-2xl font-bold text-gray-800 mb-2">
              Oops! Something went wrong
            </h1>

            <p className="text-gray-600 mb-6">
              We're sorry, but something unexpected happened. Please try reloading the application.
            </p>

            <button
              onClick={this.handleReload}
              className="w-full btn-primary font-bold py-3 text-lg"
            >
              Reload Application
            </button>

            {process.env.NODE_ENV === 'development' && this.state.error && (
              <div className="mt-6 p-4 bg-gray-100 rounded-lg text-left overflow-auto max-h-48">
                <p className="text-xs font-mono text-gray-700 break-all">
                  {this.state.error.toString()}
                </p>
              </div>
            )}
          </div>

          <div className="mt-8 text-center text-slate-500 text-sm">
            <p className="font-medium mb-1">Need help?</p>
            <p>📧 support@agridecision.tn</p>
            <p>📞 +216 71 123 456</p>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;