package com.uq.seanshi.uqfact;

import android.support.v7.app.ActionBar;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.view.MenuItem;
import android.view.View;
import android.view.inputmethod.InputMethodManager;
import android.widget.Button;
import android.widget.EditText;

/**
 * Created by seanshi on 15/5/17.
 */

public class SendFeedbackActivity extends AppCompatActivity {

    private Button sendFeedbackBtn;
    private EditText userEmail;
    private EditText userFeedback;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_feedback);

        ActionBar actionBar = getSupportActionBar();
        actionBar.setDisplayHomeAsUpEnabled(true);

        userEmail = (EditText) findViewById(R.id.emailInput);
        userFeedback = (EditText) findViewById(R.id.contentInput);
        sendFeedbackBtn = (Button) findViewById(R.id.feedBackBtn);
        sendFeedbackBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                sendMail();
            }
        });

    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        switch (item.getItemId()) {
            case android.R.id.home:
                finish();
                return true;
        }

        return super.onOptionsItemSelected(item);
    }

    private void sendMail() {
        try {
            InputMethodManager imm = (InputMethodManager)getSystemService(INPUT_METHOD_SERVICE);
            imm.hideSoftInputFromWindow(getCurrentFocus().getWindowToken(), 0);
        } catch (Exception e) {
            e.printStackTrace();
        }
        SendEmailUtil sendEmailUtil = new SendEmailUtil(userEmail.getText().toString(), userFeedback.getText().toString(), SendFeedbackActivity.this);
        try {
            sendEmailUtil.execute();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
