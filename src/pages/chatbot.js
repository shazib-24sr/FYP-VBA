// src/pages/Chatbot.js
import React from 'react';
import Navbar from '../components/ui/navbar';
import SidebarLayout from '../components/ui/sidebar';

const Chatbot = () => {
  return (
    <><Navbar/>
    <SidebarLayout>
    <div style={{ width: '100%', height: '100vh' }}>
      <iframe
        title="Botpress Chatbot"
        src="https://cdn.botpress.cloud/webchat/v3.0/shareable.html?configUrl=https://files.bpcontent.cloud/2025/06/07/17/20250607170018-0IOYNMBW.json"
        style={{
          width: '100%',
          height: '100%',
          border: 'none',
        }}
        allow="microphone; autoplay"
      />
    </div>
    </SidebarLayout>
    </>
  );
};

export default Chatbot;
