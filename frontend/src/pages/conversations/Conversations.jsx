import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Conversations() {
  const navigate = useNavigate();

  useEffect(() => {
    // Redirect to the working live chat page
    navigate('/live-chat', { replace: true });
  }, [navigate]);

  return (
    <div className="animate-fade-in flex items-center justify-center h-64">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Переход к чату...</p>
      </div>
    </div>
  );
}
