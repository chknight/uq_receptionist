package com.uq.seanshi.uqfact;

import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.os.AsyncTask;
import android.speech.RecognitionListener;
import android.speech.RecognizerIntent;
import android.support.v7.app.ActionBarActivity;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.MotionEvent;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import java.net.URLEncoder;
import java.util.ArrayList;
import java.util.Locale;
import java.util.Map;

import ai.api.AIListener;
import ai.api.AIServiceException;
import ai.api.android.AIConfiguration;
import ai.api.android.AIDataService;
import ai.api.android.AIService;
import ai.api.model.AIError;
import ai.api.model.AIRequest;
import ai.api.model.AIResponse;
import ai.api.model.Result;

import com.iflytek.cloud.ErrorCode;
import com.iflytek.cloud.InitListener;
import com.iflytek.cloud.RecognizerListener;
import com.iflytek.cloud.RecognizerResult;
import com.iflytek.cloud.SpeechConstant;
import com.iflytek.cloud.SpeechError;
import com.iflytek.cloud.SpeechRecognizer;
import com.iflytek.cloud.SpeechSynthesizer;
import com.iflytek.cloud.SpeechUtility;
import com.iflytek.cloud.SynthesizerListener;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.UnsupportedEncodingException;
import java.net.URLDecoder;
import java.net.URLEncoder;

public class MainActivity extends AppCompatActivity {

    private AIDataService aiDataService;

    private static String TAG = MainActivity.class.getSimpleName();
    // 语音听写对象
    private SpeechRecognizer mIat;
    private SpeechSynthesizer mTts;

    private Button listenButton;
    private TextView resultTextView;
    private TextView requestTextView;

    private Toast mToast;

    private final int REQ_CODE_SPEECH_INPUT = 100;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        //语音初始化，在使用应用使用时需要初始化一次就好，如果没有这句会出现10111初始化失败
        SpeechUtility.createUtility(MainActivity.this, "appid=56b0d819");

        //处理语音合成关键类
        // 使用SpeechRecognizer对象，可根据回调消息自定义界面；
        mIat = SpeechRecognizer.createRecognizer(MainActivity.this, mInitListener);
        mTts = SpeechSynthesizer.createSynthesizer(MainActivity.this, null);

        listenButton = (Button) findViewById(R.id.listenButton);
        resultTextView = (TextView) findViewById(R.id.resultTextView);
        requestTextView = (TextView) findViewById(R.id.requestTextView);

        final AIConfiguration config = new AIConfiguration("fd151bd8a1674291a82c2baa037a1a5e",
                AIConfiguration.SupportedLanguages.English,
                AIConfiguration.RecognitionEngine.System);

        aiDataService = new AIDataService(getApplicationContext(), config);

        listenButton.setOnTouchListener(new View.OnTouchListener() {
            @Override
            public boolean onTouch(View v, MotionEvent event) {

                if (event.getAction() == MotionEvent.ACTION_DOWN) {
                    Log.d("Pressed", "Button pressed");
                    setENParam();
                    int ret = mIat.startListening(mRecognizerListener);
                    System.out.println("start listening:" + ret);
                } else if (event.getAction() == MotionEvent.ACTION_UP) {

                    Log.d("Released", "Button released");
                    mIat.stopListening();
                }
                // TODO Auto-generated method stub
                return true;
            }
        });
    }

    private void showTip(String str)
    {
        mToast.setText(str);
        mToast.show();
    }

    /**
     * 初始化监听器。
     */
    private InitListener mInitListener = new InitListener() {

        @Override
        public void onInit(int code) {
            Log.d(TAG, "SpeechRecognizer init() code = " + code);
        }
    };

    // 合成- 文字转语音
    private void Text2Voice(String str) {
        // 1.创建SpeechSynthesizer对象, 第二个参数：本地合成时传InitListener
        SpeechSynthesizer mTts = SpeechSynthesizer
                .createSynthesizer(this, null);
        // 2.合成参数设置，详见《科大讯飞MSC API手册(Android)》SpeechSynthesizer 类
        mTts.setParameter(SpeechConstant.VOICE_NAME, "Catherine");// 设置发音人
        mTts.setParameter(SpeechConstant.SPEED, "50");// 设置语速
        mTts.setParameter(SpeechConstant.VOLUME, "80");// 设置音量，范围0~100
        mTts.setParameter(SpeechConstant.ENGINE_TYPE, SpeechConstant.TYPE_CLOUD); // 设置云端

        // 3.开始合成
        mTts.startSpeaking(str, new MySynListener());
    }

    // 合成监听器
    private class MySynListener implements SynthesizerListener {
        // 会话结束回调接口，没有错误时，error为null
        public void onCompleted(SpeechError error) {
        }

        // 缓冲进度回调
        // percent为缓冲进度0~100，beginPos为缓冲音频在文本中开始位置，endPos表示缓冲音频在文本中结束位置，info为附加信息。
        public void onBufferProgress(int percent, int beginPos, int endPos,
                                     String info) {
        }

        // 开始播放
        public void onSpeakBegin() {
        }

        // 暂停播放
        public void onSpeakPaused() {
        }

        // 播放进度回调
        // percent为播放进度0~100,beginPos为播放音频在文本中开始位置，endPos表示播放音频在文本中结束位置.
        public void onSpeakProgress(int percent, int beginPos, int endPos) {
        }

        // 恢复播放回调接口
        public void onSpeakResumed() {
        }

        // 会话事件回调接口
        public void onEvent(int arg0, int arg1, int arg2, Bundle arg3) {
        }

    };

    /**
     * 听写监听器。
     */
    private RecognizerListener mRecognizerListener = new RecognizerListener() {

        String voiceResult = "";

        @Override
        public void onBeginOfSpeech() {
            // 此回调表示：sdk内部录音机已经准备好了，用户可以开始语音输入
            System.out.println("开始说话");
        }

        @Override
        public void onError(SpeechError error) {
            // Tips：
            // 错误码：10118(您没有说话)，可能是录音机权限被禁，需要提示用户打开应用的录音权限。
            // 如果使用本地功能（语记）需要提示用户开启语记的录音权限。
            System.out.println(error.getPlainDescription(true));
        }

        @Override
        public void onEndOfSpeech() {
            // 此回调表示：检测到了语音的尾端点，已经进入识别过程，不再接受语音输入
            System.out.println("结束说话");
        }

        @Override
        public void onResult(RecognizerResult results, boolean isLast) {
            Log.d(TAG, results.getResultString());
            System.out.println("结果是：");
            System.out.println(results.toString());

            if (!isLast) {
                String ans = "";
                try {
                    JSONObject result = new JSONObject(results.getResultString());
                    JSONArray jsonArray = result.getJSONArray("ws");
                    for (int i = 0; i < jsonArray.length(); i++) {
                        JSONObject object = jsonArray.getJSONObject(i);
                        JSONArray array = object.getJSONArray("cw");
                        for (int j = 0; j < array.length(); j++) {
                            JSONObject obj = array.getJSONObject(j);
                            System.out.println(obj);
                            String tmp = obj.getString("w");
                            ans = ans + tmp;
                        }
                    }
                } catch (JSONException e) {
                    e.printStackTrace();
                }
                System.out.println(ans);
                voiceResult += ans;
            }

            if (isLast) {
                System.out.println("in last");
                System.out.println(results.getResultString());

                String ans = "";
                try {
                    JSONObject result = new JSONObject(results.getResultString());
                    JSONArray jsonArray = result.getJSONArray("ws");
                    for(int i=0;i<jsonArray.length();i++){
                        JSONObject object = jsonArray.getJSONObject(i);
                        JSONArray array = object.getJSONArray("cw");
                        for (int j = 0; j < array.length(); j++) {
                            JSONObject obj = array.getJSONObject(j);
                            System.out.println(obj);
                            String tmp = obj.getString("w");
                            ans = ans + tmp;
                        }
                    }

                    voiceResult += ans;
//                    try {
//                        ans = URLEncoder.encode(voiceResult, "utf-8"); //先对中文进行UTF-8编码
//                    } catch (UnsupportedEncodingException e) {
//                        e.printStackTrace();
//                    }
                    System.out.println("request string: " + voiceResult);
                    final AIRequest aiRequest = new AIRequest();
                    aiRequest.setQuery(voiceResult);
                    requestTextView.setText("request: "+voiceResult);
                    new AsyncTask<AIRequest, Void, AIResponse>() {
                        @Override
                        protected AIResponse doInBackground(AIRequest... requests) {
                            final AIRequest request = requests[0];
                            try {
                                final AIResponse response = aiDataService.request(aiRequest);
                                return response;
                            } catch (AIServiceException e) {
                            }
                            return null;
                        }
                        @Override
                        protected void onPostExecute(AIResponse aiResponse) {
                            if (aiResponse != null) {
                                // process aiResponse here
                                resultTextView.setText(aiResponse.getResult().getFulfillment().getSpeech());
                                System.out.println("response Intent: " + aiResponse.getResult().getMetadata().getIntentName());
                                System.out.println("response Intent: " + aiResponse.getResult().getResolvedQuery());
                                Text2Voice(aiResponse.getResult().getFulfillment().getSpeech());
                            }
                        }
                    }.execute(aiRequest);
                    voiceResult = "";
                } catch (JSONException e) {
                    e.printStackTrace();
                }
            }
        }

        @Override
        public void onVolumeChanged(int volume, byte[] data) {
            System.out.println("当前正在说话，音量大小：" + volume);
            Log.d(TAG, "返回音频数据：" + data.length);
        }

        @Override
        public void onEvent(int eventType, int arg1, int arg2, Bundle obj) {
            // 以下代码用于获取与云端的会话id，当业务出错时将会话id提供给技术支持人员，可用于查询会话日志，定位出错原因
            // 若使用本地能力，会话id为null
            //	if (SpeechEvent.EVENT_SESSION_ID == eventType) {
            //		String sid = obj.getString(SpeechEvent.KEY_EVENT_SESSION_ID);
            //		Log.d(TAG, "session id =" + sid);
            //	}
        }
    };

    public void setENParam() {
        // 清空参数
        mIat.setParameter(SpeechConstant.PARAMS, null);

        mIat.setParameter(SpeechConstant.DOMAIN, "iat");
        // 设置语言
        mIat.setParameter(SpeechConstant.LANGUAGE, "en_us");
        // 设置语言区域
//        mIat.setParameter(SpeechConstant.ACCENT, "mandarin");
    }


}
