import { createContext, useContext, useState } from "react";

const FileContext = createContext(null);

export function FileProvider({ children }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadResult, setUploadResult] = useState(null);

  const value = {
    selectedFile,
    setSelectedFile,
    uploadResult,
    setUploadResult,
  };

  return (
    <FileContext.Provider value={value}>
      {children}
    </FileContext.Provider>
  );
}

export function useFile() {
  const context = useContext(FileContext);

  if (!context) {
    throw new Error("useFile must be used inside a FileProvider");
  }

  return context;
}