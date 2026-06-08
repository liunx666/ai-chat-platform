/**
 * @file AI聊天接口
 * @description 封装AI对话流式接口和保存回复接口
 * @author aichat_upend
 */

import { request, streamRequest } from '@/utils/request';

function chat(params, callback) {
  const url = new URLSearchParams();
  url.append('question', params.question);
  if (params.conversation_id) {
    url.append('conversation_id', params.conversation_id);
  }
  if (params.isThinking !== undefined) {
    url.append('isThinking', params.isThinking);
  }

  const baseURL = streamRequest.defaults.baseURL;
  const xhr = new XMLHttpRequest();
  xhr.open('POST', `${baseURL}/chat?${url.toString()}`, true);

  let lastIndex = 0;

  const token = localStorage.getItem('token');
  if (token) {
    xhr.setRequestHeader('Authorization', `Bearer ${token}`);
  }
  xhr.setRequestHeader('Content-Type', 'application/json');

  xhr.onprogress = (event) => {
    if (event.lengthComputable || event.target.responseText) {
      const fullResponse = event.target.responseText;
      const newContent = fullResponse.slice(lastIndex);
      lastIndex = fullResponse.length;
      if (callback && newContent) {
        callback(newContent);
      }
    }
  };

  xhr.onload = () => {
    if (xhr.status >= 200 && xhr.status < 300) {
      try {
        const responseText = xhr.responseText;
        const lines = responseText.split('\n').filter(line => line.trim());
        for (const line of lines) {
          if (line === '[DONE]') continue;
          if (line.startsWith('data:')) {
            const jsonStr = line.slice(5).trim();
            if (!jsonStr || jsonStr === '[DONE]') continue;
            try {
              const data = JSON.parse(jsonStr);
              if (callback) {
                callback(`data:${JSON.stringify({ ...data, end: false })}\n`);
              }
            } catch (e) {
              console.error('[Chat Parse Line Error]:', e);
            }
          }
        }
        if (callback) {
          callback(`data:${JSON.stringify({ end: true })}\n`);
        }
      } catch (e) {
        console.error('[Chat Parse Error]:', e);
      }
    } else {
      console.error('[Chat Error]:', xhr.statusText);
    }
  };

  xhr.onerror = (error) => {
    console.error('[Chat Network Error]:', error);
  };

  xhr.send();
  return xhr;
}

export { chat };
