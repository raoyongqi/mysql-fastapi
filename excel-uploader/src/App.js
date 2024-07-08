import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [file, setFile] = useState(null);
  const [filename, setFilename] = useState('');
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:8000/upload_excel/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setFilename(response.data.filename);
      setError('');
    } catch (error) {
      console.error('Error uploading file:', error);
      setError('Error uploading file: ' + error.message);
    }
  };

  return (
    <div className="App">
      <h1>Upload Excel File</h1>
      <form onSubmit={handleSubmit}>
        <input type="file" accept=".xlsx, .xls" onChange={handleFileChange} />
        <button type="submit">Upload</button>
      </form>
      {filename && <p>Uploaded File: {filename}</p>}
      {error && <p style={{color: 'red'}}>{error}</p>}
    </div>
  );
}

export default App;
