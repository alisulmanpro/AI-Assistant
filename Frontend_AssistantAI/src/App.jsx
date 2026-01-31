import { useRef, useState } from 'react'
import './App.css'
import '@chatscope/chat-ui-kit-styles/dist/default/styles.min.css';
import { MainContainer, ChatContainer, MessageList, Message, MessageInput, TypingIndicator, ConversationHeader, Avatar, Sidebar, ExpansionPanel, Status } from '@chatscope/chat-ui-kit-react';
import { AudioRecorder, useAudioRecorder } from 'react-audio-voice-recorder';
import languages from './constants'
import FileSaver from 'file-saver';
// "Explain things like you would to a 10 year old learning how to code."
const systemMessage = { //  Explain things like you're talking to a software professional with 5 years of experience.
  "role": "system", "content": "Explain things like you're talking to a software professional with 2 years of experience."
}

function App() {
  const recorderControls = useAudioRecorder();
  const [messages, setMessages] = useState([
    {
      message: "Hello, I'm AssistantAI! Ask me anything!",
      sentTime: "just now",
      sender: "AssistantAI"
    }
  ]);
  const [isTyping, setIsTyping] = useState(false);
  const [language, setLanguage] = useState("English");
  const [bot, setBot] = useState("travel_bot");
  const msgListRef = useRef();

  const handleSend = async (message) => {
    const newMessage = {
      message,
      direction: 'outgoing',
      sender: "user"
    };

    const newMessages = [...messages, newMessage];
    
    setMessages(newMessages);

    // Initial system message to determine ChatGPT functionality
    // How it responds, how it talks, etc.
    setIsTyping(true);
    await processMessageToChatGPT(newMessage, newMessages);
  };

  async function processMessageToChatGPT(chatMessage, allMessages) { 
    // Get the request body set up with the model we plan to use
    // and the messages which we formatted above. We add a system message in the front to'
    // determine how we want chatGPT to act. 
    const apiRequestBody = {
      "message": chatMessage.message,
      "language": language,
      "bot_name": bot,
      "audio": ""
    }

    await fetch("http://127.0.0.1:5600", 
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(apiRequestBody)
    }).then((data) => {
      return data.json();
    }).then((data) => {
      console.log(data);
      if(!data.error){
        setTimeout(()=>{
          setMessages([...allMessages, {
            message: data.message,
            sender: "ChatGPT",
            sentiments: data.sentiments,
          }]);
          msgListRef.current.scrollToBottom("auto");
          setIsTyping(false);
        }, 3000);
      } else {
        setIsTyping(false);
      }
    });
  }

//   const saveBlob = (function () {
//     var a = document.createElement("a");
//     document.body.appendChild(a);
//     a.style = "display: none";
//     return function (blob, fileName) {

//         var reader = new FileReader();
//       reader.readAsDataURL(blob);
//       reader.onloadend = function () {
//               var base64String = reader.result;
//               console.log('Base64 String - ', base64String);
//               console.log('Base64 String without Tags- ', 
//             base64String.substr(base64String.indexOf(', ') + 1));
//           }

//         var url = window.URL.createObjectURL(blob);
//         a.href = url;
//         a.download = fileName;
//         a.click();
//         window.URL.revokeObjectURL(url);
//     };
// }());

  const saveBlob = async (blob) => {
    try {
      FileSaver.saveAs(blob, 'audio.wav');
    } catch (error) {
      console.log(error);
    }
  }

  const addAudioElement = async (blob) => {
    // const audioData = await blob.text();
    // console.log(audioData)
    await saveBlob(blob);
    const url = URL.createObjectURL(blob);  
    const audio = document.createElement('audio');
    audio.src = url;
    audio.controls = true;
    document.body.appendChild(audio);
  };
 
  return (
    <div className="App">
      <div class="absolute top-0 text-left z-[-1] m-8">
        <span class='font-extrabold	 text-lg dark:text-white'>Welcome to AI Assistant.</span>
      </div>
      <div  style={{ position:"relative", height: "800px", width: "100%"  }}>
        <MainContainer className='dark-bg-black'>
          <Sidebar position='left' className='dark-bg-black'>
            <ExpansionPanel title='Language Select'>
              <select className='dark:bg-slate-800' defaultValue={language} onChange={(e) => setLanguage(e.target.value)}>
                {languages.map((language, i) => 
                  <option key={i} value={language}>{language}</option>
                )}
              </select>
            </ExpansionPanel>
            <ExpansionPanel title='Bot Select'>
              <div onChange={(e) => setBot(e.target.value)} style={{display: 'flex', justifyContent: 'space-around'}}>
                <input type='radio' value="travel_bot" name='bot_select' defaultChecked/> Travel Bot
                <input type='radio' value="education_bot" name='bot_select' />Education Bot
              </div>
            </ExpansionPanel>
          </Sidebar>
          <ChatContainer>    
            <ConversationHeader>
              <Avatar src='/bot.png' name="bot" >
              </Avatar>
              <ConversationHeader.Content><span className='font-semibold dark:text-white' style={{ display: "flex"}}>Ask me anything</span></ConversationHeader.Content>
            </ConversationHeader>   
            <MessageList 
              typingIndicator={isTyping ? <TypingIndicator content="AssistantAI is typing" /> : null}
              ref={msgListRef}
              scrollBehavior={"auto"}
            >
              {messages.map((message, i) => {
                console.log(message)
                return <Message key={i} model={message} > <Avatar src={message.sender == 'user' ? '/user1.png' : '/bot.png'} name="bot" />
                  {message.sender != 'user' && i !== 0 ? <Message.Footer>sentiments: {message.sentiments}</Message.Footer> : <></>}
                 </Message>
              })}
            </MessageList>
            <MessageInput placeholder="Type message here" onSend={handleSend} />    
                
          </ChatContainer>
          {/* <AudioRecorder
            onRecordingComplete={(blob) => addAudioElement(blob)}
            recorderControls={recorderControls}
          /> */}
          <div className="absolute top-5 right-0 z-[2]">
            <svg
              width="238"
              height="531"
              viewBox="0 0 238 531"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <rect
                opacity="0.3"
                x="422.819"
                y="-70.8145"
                width="196"
                height="541.607"
                rx="2"
                transform="rotate(51.2997 422.819 -70.8145)"
                fill="url(#paint0_linear_83:2)"
              />
              <rect
                opacity="0.3"
                x="426.568"
                y="144.886"
                width="59.7544"
                height="541.607"
                rx="2"
                transform="rotate(51.2997 426.568 144.886)"
                fill="url(#paint1_linear_83:2)"
              />
              <defs>
                <linearGradient
                  id="paint0_linear_83:2"
                  x1="517.152"
                  y1="-251.373"
                  x2="517.152"
                  y2="459.865"
                  gradientUnits="userSpaceOnUse"
                >
                  <stop stopColor="#4A6CF7" />
                  <stop offset="1" stopColor="#4A6CF7" stopOpacity="0" />
                </linearGradient>
                <linearGradient
                  id="paint1_linear_83:2"
                  x1="455.327"
                  y1="-35.673"
                  x2="455.327"
                  y2="675.565"
                  gradientUnits="userSpaceOnUse"
                >
                  <stop stopColor="#4A6CF7" />
                  <stop offset="1" stopColor="#4A6CF7" stopOpacity="0" />
                </linearGradient>
              </defs>
            </svg>
          </div>
        </MainContainer>
      </div>
      
      <div className="absolute bottom-0 left-0 right-0 z-[-1]">
        <img src="/shape.svg" alt="shape" className="w-full" />
      </div>
    </div>
  )
}

export default App
