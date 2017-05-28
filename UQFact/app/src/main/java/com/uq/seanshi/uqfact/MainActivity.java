package com.uq.seanshi.uqfact;

import android.app.Activity;
import android.app.ListActivity;
import android.app.ProgressDialog;
import android.content.Context;
import android.content.Intent;
import android.graphics.PorterDuff;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.os.AsyncTask;
import android.speech.RecognitionListener;
import android.speech.RecognizerIntent;
import android.support.v7.app.ActionBarActivity;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.telephony.TelephonyManager;
import android.util.Log;
import android.view.Menu;
import android.view.MenuInflater;
import android.view.MenuItem;
import android.view.MotionEvent;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;

import ai.api.AIListener;
import ai.api.AIServiceException;
import ai.api.android.AIConfiguration;
import ai.api.android.AIDataService;
import ai.api.android.AIService;
import ai.api.model.AIContext;
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

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ExecutionException;

public class MainActivity extends AppCompatActivity {

    private AIDataService aiDataService;

    private static String TAG = MainActivity.class.getSimpleName();
    // 语音听写对象
    private SpeechRecognizer mIat;
    private SpeechSynthesizer mTts;

    private Button listenButton;
    private Button submitQueryButton;
    private EditText requestTextView;
    private ListView listView;

    private ChatArrayAdapter chatArrayAdapter;

    private Toast mToast;

    private boolean trainMode = false;
    private boolean serverStatus = true;

    private final String initHintMessage = "Hi, I am your UQ chatbot, you can ask me questions about UQ like: \n" +
            "what program do you have? what is UQ? where is school of business? entry requirement of master of data science?\n" +
            "For more information, please read through the user guide or send us feedback by clicking the button on the top right corner";
    private String lastRequestQuery;
    private String lastRequestQueryAnswer;
    private String deviceId;

    private List<AIContext> contexts;

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        MenuInflater inflater = getMenuInflater();
        inflater.inflate(R.menu.menu, menu);
        return super.onCreateOptionsMenu(menu);
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        int id = item.getItemId();

        switch (id) {
            case R.id.sendFeedback:
                startActivity(new Intent(this, SendFeedbackActivity.class));
                return true;
            case R.id.userGuide:
                startActivity(new Intent(this, UserGuideActivity.class));
                return true;
        }

        return super.onOptionsItemSelected(item);
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        setSessionUsingDeviceID();

        //语音初始化，在使用应用使用时需要初始化一次就好，如果没有这句会出现10111初始化失败
        SpeechUtility.createUtility(MainActivity.this, "appid=56b0d819");

        //处理语音合成关键类
        // 使用SpeechRecognizer对象，可根据回调消息自定义界面；
        mIat = SpeechRecognizer.createRecognizer(MainActivity.this, mInitListener);
        mTts = SpeechSynthesizer.createSynthesizer(MainActivity.this, null);

        listenButton = (Button) findViewById(R.id.listenButton);
        submitQueryButton = (Button) findViewById(R.id.submit);
        requestTextView = (EditText) findViewById(R.id.requestTextView);
        listView = (ListView) findViewById(R.id.listView);

        chatArrayAdapter = new ChatArrayAdapter(this, R.layout.right, mTts);
        listView.setAdapter(chatArrayAdapter);

        //init hint message
        chatArrayAdapter.add(new ChatMessage(false, initHintMessage));
        Text2Voice(initHintMessage);

        final AIConfiguration config = new AIConfiguration("fd151bd8a1674291a82c2baa037a1a5e",
                AIConfiguration.SupportedLanguages.English,
                AIConfiguration.RecognitionEngine.System);

        aiDataService = new AIDataService(getApplicationContext(), config);

        submitQueryButton.setOnTouchListener(new View.OnTouchListener() {
            @Override
            public boolean onTouch(View view, MotionEvent event) {
                switch (event.getAction()) {
                    case MotionEvent.ACTION_DOWN: {
                        view.getBackground().setColorFilter(0xe0f47521, PorterDuff.Mode.SRC_ATOP);
                        view.invalidate();
                        String query = requestTextView.getText().toString();
                        if (!query.equals("")) {
                            sendRequestAndHandleResponse(query, false);
                        }
                        break;
                    }
                    case MotionEvent.ACTION_UP: {
                        view.getBackground().clearColorFilter();
                        view.invalidate();
                        break;
                    }
                }
                return true;
            }
        });

        listenButton.setOnTouchListener(new View.OnTouchListener() {
            @Override
            public boolean onTouch(View v, MotionEvent event) {

                if (event.getAction() == MotionEvent.ACTION_DOWN) {
                    Log.d("Pressed", "Button pressed");
                    listenButton.setText("Keep Speaking, I'm listening");
                    setENParam();
                    int ret = mIat.startListening(mRecognizerListener);
                    System.out.println("start listening:" + ret);
                } else if (event.getAction() == MotionEvent.ACTION_UP) {
                    listenButton.setText("CLICK TO SPEAK");
                    Log.d("Released", "Button released");
                    mIat.stopListening();
                }
                // TODO Auto-generated method stub
                return true;
            }
        });

        checkServerStatus();

    }

    private void showTip(String str) {
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
        mTts = SpeechSynthesizer
                .createSynthesizer(this, null);
        // 2.合成参数设置，详见《科大讯飞MSC API手册(Android)》SpeechSynthesizer 类
        mTts.setParameter(SpeechConstant.VOICE_NAME, "Catherine");// 设置发音人
        mTts.setParameter(SpeechConstant.SPEED, "50");// 设置语速
        mTts.setParameter(SpeechConstant.VOLUME, "80");// 设置音量，范围0~100
        mTts.setParameter(SpeechConstant.ENGINE_TYPE, SpeechConstant.TYPE_CLOUD); // 设置云端

        // 3.开始合成
        mTts.startSpeaking(str, new MySynListener());
    }

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

                    voiceResult += ans;
                    System.out.println("request string: " + voiceResult);
                    requestTextView.setText(voiceResult);

//                    if (!trainMode) {
//                        sendRequestAndHandleResponse(voiceResult, false);
//                    }
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

    private boolean updateView(String response) {
        chatArrayAdapter.add(new ChatMessage(false, response));
        requestTextView.setText("");
        return true;
    }

    private boolean checkServerStatus() {
        GetAsyncTask asyncT = new GetAsyncTask();
        try {
            ConnectivityManager conMgr = (ConnectivityManager)getSystemService(Context.CONNECTIVITY_SERVICE);
            if (conMgr.getNetworkInfo(ConnectivityManager.TYPE_MOBILE).getState() == NetworkInfo.State.DISCONNECTED
                    && conMgr.getNetworkInfo(ConnectivityManager.TYPE_WIFI).getState() == NetworkInfo.State.DISCONNECTED) {
                mToast = Toast.makeText(this, "Please check your internet connection", Toast.LENGTH_LONG);
                mToast.show();
                serverStatus = false;
                return false;
            }
            String response = asyncT.execute().get();
            if (!response.equals("Success")) {
                mToast = Toast.makeText(this, "Server is now under maintenance, please use the app later", Toast.LENGTH_LONG);
                mToast.show();
                serverStatus = false;
                return false;
            }
        } catch (InterruptedException e) {
            e.printStackTrace();
        } catch (ExecutionException e) {
            e.printStackTrace();
        }
        return true;
    }

    private void startSelfTrain(AIResponse response) {
        String newResponse = response.getResult().getFulfillment().getSpeech() + "Would you be able to tell me the correct answer?";
        chatArrayAdapter.add(new ChatMessage(false, true, newResponse));
        Text2Voice(newResponse);
        requestTextView.setText("");
    }

    private void startAskNationality(AIResponse response) {
        String newResponse = response.getResult().getFulfillment().getSpeech();
        chatArrayAdapter.add(new ChatMessage(false, true, true, newResponse));
        Text2Voice(newResponse);
        requestTextView.setText("");
    }

    private boolean sendPost(Map<String, String> map) {
        PostAsyncTask asyncT = new PostAsyncTask(map);
        try {
            String response = asyncT.execute().get();
            if (response.equals("Success")) {
                return true;
            }
        } catch (InterruptedException e) {
            e.printStackTrace();
        } catch (ExecutionException e) {
            e.printStackTrace();
        }
        return false;
    }

    private void setSessionUsingDeviceID() {
        TelephonyManager telephonyManager = (TelephonyManager) getSystemService(Context.TELEPHONY_SERVICE);
        deviceId = telephonyManager.getDeviceId();
        contexts = new ArrayList<>();
        AIContext deviceContext = new AIContext("deviceContext");
        Map<String, String> map = new HashMap<>();
        map.put("deviceId", deviceId);
        deviceContext.setParameters(map);
        contexts.add(deviceContext);
        System.out.println(deviceId);
    }

    private void sendRequestAndHandleResponse(String query, Boolean isHidenRequest) {
        if (!serverStatus) {
            mToast = Toast.makeText(this, "Check your internet connection or server is under maintenance, please try later", Toast.LENGTH_LONG);
            mToast.show();
            return;
        }
        final AIRequest aiRequest = new AIRequest();
        if (!isHidenRequest) {
            chatArrayAdapter.add(new ChatMessage(true, query));
        }

        if (trainMode) {
            lastRequestQueryAnswer = query;
            //send to server and store
            System.out.print("stored last query:" + lastRequestQuery);
            System.out.print("stored last answer:" + lastRequestQueryAnswer);
            Map<String, String> map = new HashMap<String, String>();
            map.put("url", "selftraining");
            map.put("question", lastRequestQuery);
            map.put("answer", lastRequestQueryAnswer);
            sendPost(map);
            trainMode = false;
            requestTextView.setText("");
            String speech = "Thank you very much, your reply is now stored in the database";
            chatArrayAdapter.add(new ChatMessage(false, speech));
            Text2Voice(speech);
            return;
        }

        aiRequest.setQuery(query);
        aiRequest.setContexts(contexts);
        lastRequestQuery = query;
//        findViewById(R.id.loadingPanel).setVisibility(View.GONE);
        new AsyncTask<AIRequest, Void, AIResponse>() {
            ProgressDialog progDailog;
            @Override
            protected void onPreExecute() {
                super.onPreExecute();
                progDailog = new ProgressDialog(MainActivity.this);
                progDailog.setMessage("Fetching Answer...");
                progDailog.setIndeterminate(false);
                progDailog.setProgressStyle(ProgressDialog.STYLE_SPINNER);
                progDailog.setCancelable(true);
                progDailog.show();
            }
            @Override
            protected AIResponse doInBackground(AIRequest... requests) {
                final AIRequest request = requests[0];
                try {
                    final AIResponse response = aiDataService.request(aiRequest);
                    return response;
                } catch (AIServiceException e) {
                    e.printStackTrace();
                }
                return null;
            }

            @Override
            protected void onPostExecute(AIResponse aiResponse) {
                progDailog.dismiss();
                if (aiResponse != null) {
                    // process aiResponse here
                    System.out.println("response Intent: " + aiResponse.getResult().getMetadata().getIntentName());
                    System.out.println("response Intent: " + aiResponse.getResult().getResolvedQuery());
                    //self train
                    if (aiResponse.getResult().getFulfillment().getSpeech().contains("Sorry, we could not answer this question.")) {
                        startSelfTrain(aiResponse);
                        return;
                    }
                    //ask for nationality
                    if (aiResponse.getResult().getFulfillment().getSpeech().contains("Are you an international student?")) {
                        startAskNationality(aiResponse);
                        return;
                    }
                    String voiceResponse = aiResponse.getResult().getFulfillment().getSpeech();
                    updateView(voiceResponse);
                    Text2Voice(voiceResponse);
                }
            }
        }.execute(aiRequest);
    }

    //self train
    public void YesSelfTrain() {
        String bad = "Great, I'm ready to learn";
        chatArrayAdapter.add(new ChatMessage(false, bad));
        Text2Voice(bad);
        requestTextView.setText("");
        trainMode = true;
    }

    public void NotSelfTrain() {
        String bad = "That's alright, you can still try some other questions";
        chatArrayAdapter.add(new ChatMessage(false, bad));
        Text2Voice(bad);
        requestTextView.setText("");
    }

    //ask nationality
    public void InternationalStudent() {
        Map<String, String> map = new HashMap<>();
        map.put("url", "nationality");
        map.put("nationality", "1");
        map.put("deviceId", deviceId);
        Boolean isFinished = sendPost(map);
        if (isFinished) {
            chatArrayAdapter.add(new ChatMessage(false, "Thank you, I am now fetching the answer of your previous question"));
            sendRequestAndHandleResponse(lastRequestQuery, true);
        }
    }

    public void DomesticStudent() {
        Map<String, String> map = new HashMap<>();
        map.put("url", "nationality");
        map.put("nationality", "0");
        map.put("deviceId", deviceId);
        Boolean isFinished = sendPost(map);
        if (isFinished) {
            chatArrayAdapter.add(new ChatMessage(false, "Thank you, I am now fetching the answer of your previous question"));
            sendRequestAndHandleResponse(lastRequestQuery, true);
        }
    }

}
