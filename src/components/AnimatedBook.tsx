import React, { useState, useEffect, useCallback } from 'react';

// Minecraft Galactic Alphabet content to write in the book
const bookContent = [
  "ᓭℸ ̣ ᔑ∷ℸ ̣ ||¡∷ ᔑ↸⍊ᒷリℸ ̣ ⚍∷ᒷ", // START YOUR ADVENTURE  
  "∴╎ℸ ̣ ⍑ ᔑ╎ ᔑᓭᓭ╎ᓭℸ ̣ ᔑリᓵᒷ", // WITH AI ASSISTANCE
  "ᓵ∷ᒷᔑℸ ̣ ᒷ ᒲᔑ⊣╎ᓵᔑꖎ ᓭℸ ̣ ∷╎ᒷᓭ", // CREATE MAGICAL STORIES
  "∴∷╎ℸ ̣ ᒷ ᒷ!¡╎ᓵ ℸ ̣ ᔑꖎᒷᓭ", // WRITE EPIC TALES
  "!¡ᔑ⊣ᒷ ᔑ⎓ℸ ̣ ᒷ∷ !¡ᔑ⊣ᒷ", // PAGE AFTER PAGE
  "ᒷリ↸ꖎᒷᓭᓭ !¡ᓭᓭ╎ʖ╎ꖎ╎ℸ ̣ ╎ᒷᓭ" // ENDLESS POSSIBILITIES
];

interface AnimatedBookProps {
  className?: string;
}

const AnimatedBook: React.FC<AnimatedBookProps> = ({ className = "" }) => {
  const [currentLine, setCurrentLine] = useState(0);
  const [currentChar, setCurrentChar] = useState(0);
  const [writtenText, setWrittenText] = useState<string[]>([]);
  const [isFlipping, setIsFlipping] = useState(false);
  const [animationSpeed, setAnimationSpeed] = useState(1);
  const [clickCount, setClickCount] = useState(0);
  const [lastClickTime, setLastClickTime] = useState(0);
  const [currentPage, setCurrentPage] = useState<'left' | 'right'>('left');

  // Writing animation
  useEffect(() => {
    const interval = setInterval(() => {
      const currentLineText = bookContent[currentLine];
      
      if (currentChar < currentLineText.length) {
        // Continue writing current line
        setCurrentChar(prev => prev + 1);
      } else {
        // Move to next line
        setWrittenText(prev => {
          const newText = [...prev];
          newText[currentLine] = currentLineText;
          return newText;
        });
        
        if (currentLine < bookContent.length - 1) {
          setCurrentLine(prev => prev + 1);
          setCurrentChar(0);
          // Switch to right page after 3 lines
          if (currentLine === 2 && currentPage === 'left') {
            setCurrentPage('right');
          }
        } else {
          // Finished writing all lines, flip page and start over
          setIsFlipping(true);
          setTimeout(() => {
            setCurrentLine(0);
            setCurrentChar(0);
            setWrittenText([]);
            setCurrentPage('left');
            setIsFlipping(false);
          }, 1500); // Longer flip animation
        }
      }
    }, 100 / animationSpeed);

    return () => clearInterval(interval);
  }, [currentLine, currentChar, animationSpeed, currentPage]);

  // Reset speed after inactivity
  useEffect(() => {
    if (clickCount > 0) {
      const resetTimer = setTimeout(() => {
        setAnimationSpeed(1);
        setClickCount(0);
      }, 5000);

      return () => clearTimeout(resetTimer);
    }
  }, [lastClickTime, clickCount]);

  const handleBookClick = useCallback(() => {
    const now = Date.now();
    setLastClickTime(now);
    setClickCount(prev => prev + 1);
    
    // Increase speed up to 3x with spam clicks
    const newSpeed = Math.min(1 + (clickCount * 0.5), 3);
    setAnimationSpeed(newSpeed);
  }, [clickCount]);

  // Calculate quill position based on current page
  const getQuillPosition = () => {
    const lineHeight = 30; // Match the line spacing
    const charWidth = 8;   // Adjust for better character spacing
    const leftPageStartX = 40;  // Start after red margin
    const rightPageStartX = 220; // Right page start
    const startY = 60;     // Match the first line position
    
    const adjustedLine = currentPage === 'left' ? currentLine : currentLine - 3;
    const startX = currentPage === 'left' ? leftPageStartX : rightPageStartX;
    
    return {
      x: startX + (currentChar * charWidth),
      y: startY + (adjustedLine * lineHeight)
    };
  };

  const quillPos = getQuillPosition();
  
  // Calculate glow intensity based on written text
  const totalCharsWritten = writtenText.reduce((sum, line) => sum + line.length, 0) + currentChar;
  const glowIntensity = Math.min(totalCharsWritten / 50, 1); // Max glow at 50 characters

  return (
    <div className={`relative ${className}`}>
      <div 
        className="relative cursor-pointer select-none"
        onClick={handleBookClick}
      >
        {/* Book with increasing glow */}
        <div 
          className={`relative w-96 h-96 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg border-4 border-blue-200 transform transition-all duration-1000 ${isFlipping ? 'rotateY-180 scale-95' : ''}`}
          style={{
            boxShadow: `0 0 ${30 + glowIntensity * 60}px rgba(59, 130, 246, ${0.4 + glowIntensity * 0.7}), 0 15px 40px rgba(0, 0, 0, 0.2)`,
            transformStyle: 'preserve-3d'
          }}
        >
          {/* Book spine shadow */}
          <div className="absolute left-0 top-0 w-4 h-full bg-gradient-to-r from-blue-300 to-blue-200 rounded-l-lg"></div>
          <div className="absolute left-1/2 top-0 w-2 h-full bg-blue-300 shadow-inner"></div>
          
          {/* Page content area */}
          <div className="relative p-4 h-full overflow-hidden flex">
            {/* Left Page */}
            <div className="flex-1 relative">
              {/* Blue lined paper background */}
              <div className="absolute inset-0 bg-white rounded-r-sm">
                {[...Array(10)].map((_, i) => (
                  <div 
                    key={i}
                    className="absolute w-full h-px bg-blue-300"
                    style={{ top: `${60 + i * 30}px` }}
                  />
                ))}
                {/* Red margin line */}
                <div className="absolute left-8 top-0 w-px h-full bg-red-400"></div>
              </div>
              
              {/* Left page text */}
              {writtenText.slice(0, 3).map((line, index) => (
                <div 
                  key={index}
                  className="absolute text-blue-900 font-mono text-xs z-5"
                  style={{ 
                    top: `${60 + index * 30}px`,
                    left: '40px',
                    lineHeight: '30px'
                  }}
                >
                  {line}
                </div>
              ))}
              
              {/* Current line being written on left page */}
              {currentLine < 3 && (
                <div 
                  className="absolute text-blue-900 font-mono text-xs z-5"
                  style={{ 
                    top: `${60 + currentLine * 30}px`,
                    left: '40px',
                    lineHeight: '30px'
                  }}
                >
                  {bookContent[currentLine]?.slice(0, currentChar)}
                </div>
              )}
            </div>

            {/* Right Page */}
            <div className="flex-1 relative">
              {/* Blue lined paper background */}
              <div className="absolute inset-0 bg-white rounded-l-sm">
                {[...Array(10)].map((_, i) => (
                  <div 
                    key={i}
                    className="absolute w-full h-px bg-blue-300"
                    style={{ top: `${60 + i * 30}px` }}
                  />
                ))}
                {/* Red margin line */}
                <div className="absolute left-8 top-0 w-px h-full bg-red-400"></div>
              </div>
              
              {/* Right page text */}
              {writtenText.slice(3).map((line, index) => (
                <div 
                  key={index + 3}
                  className="absolute text-blue-900 font-mono text-xs z-5"
                  style={{ 
                    top: `${60 + index * 30}px`,
                    left: '40px',
                    lineHeight: '30px'
                  }}
                >
                  {line}
                </div>
              ))}
              
              {/* Current line being written on right page */}
              {currentLine >= 3 && (
                <div 
                  className="absolute text-blue-900 font-mono text-xs z-5"
                  style={{ 
                    top: `${60 + (currentLine - 3) * 30}px`,
                    left: '40px',
                    lineHeight: '30px'
                  }}
                >
                  {bookContent[currentLine]?.slice(0, currentChar)}
                </div>
              )}
            </div>

            {/* Animated quill - positioned above text */}
            <div 
              className="absolute transition-all duration-150 ease-linear pointer-events-none z-20"
              style={{
                transform: `translate(${quillPos.x}px, ${quillPos.y}px)`,
              }}
            >
              {/* Quill feather */}
              <div className="relative">
                <div className="w-6 h-1 bg-gradient-to-r from-amber-700 to-amber-900 rounded-full transform rotate-12"></div>
                <div className="absolute -top-1 -left-1 w-2 h-3 bg-blue-600 rounded-full shadow-lg"></div>
                
                {/* Ink drops/splotches */}
                <div className="absolute -bottom-1 left-2 w-1 h-1 bg-blue-600 rounded-full opacity-80"></div>
                <div className="absolute -bottom-2 left-1 w-0.5 h-0.5 bg-blue-700 rounded-full opacity-60"></div>
                <div className="absolute -bottom-1 left-3 w-0.5 h-0.5 bg-blue-500 rounded-full opacity-40"></div>
              </div>
            </div>

            {/* Ink trail behind the quill */}
            {currentChar > 0 && (
              <div 
                className="absolute pointer-events-none z-5"
                style={{
                  transform: `translate(${quillPos.x - 8}px, ${quillPos.y + 2}px)`,
                }}
              >
                <div className="w-1 h-1 bg-blue-600 rounded-full opacity-50 animate-pulse"></div>
              </div>
            )}

            {/* Magical particles */}
            <div className="absolute inset-0 pointer-events-none overflow-hidden z-5">
              {[...Array(Math.floor(4 + glowIntensity * 8))].map((_, i) => (
                <div
                  key={i}
                  className="absolute w-1 h-1 bg-blue-400 rounded-full animate-pulse"
                  style={{
                    top: `${Math.random() * 80 + 10}%`,
                    left: `${Math.random() * 80 + 10}%`,
                    animationDelay: `${i * 0.4}s`,
                    animationDuration: `${1.5 + Math.random()}s`,
                    opacity: 0.4 + glowIntensity * 0.6
                  }}
                />
              ))}
            </div>
          </div>
        </div>
      </div>
      
      {/* Speed indicator */}
      {animationSpeed > 1 && (
        <div className="absolute -bottom-8 left-1/2 transform -translate-x-1/2 text-cosmic-bright text-xs font-medium">
          Speed: {animationSpeed.toFixed(1)}x
        </div>
      )}
    </div>
  );
};

export default AnimatedBook;