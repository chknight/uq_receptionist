package com.uq.seanshi.uqfact;

import android.support.v7.app.ActionBar;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.MenuItem;
import android.widget.TextView;

public class UserGuideActivity extends AppCompatActivity {

    private TextView userGuide;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_user_guide);

        ActionBar actionBar = getSupportActionBar();
        actionBar.setDisplayHomeAsUpEnabled(true);

        userGuide = (TextView) findViewById(R.id.userGuide);
        String userGuideText = "Currently we have the following features:\n"+
                "1. Ask for course description like: what is software process?\n"+
                "2. Ask for the location of uq faculty like : where is school of business?\n"+
                "3. Ask about the lecturer teaching which course like: who teach engineering design?\n"+
                "4. Ask about entry requirement for a program like: entry requirement of bachelor of information technology?\n"+
                "5. Ask about course list for a program like: what course will I learn in master of data science?\n"+
                "6. Ask about program duration like: what is the length of bachelor of commerce?\n"+
                "7. Ask about program cost like: tuition fee of master of computer science?\n"+
                "8. Ask about general questions related to uq like: what is a program? where to get student ID card? what banks are on campus? where is gatton campus? A full list of current support general questions can be found at UQ Answers (https://uqcurrent.custhelp.com/app)\n"+
                "Note: The first time you ask a question related to a program, we need to gather the information whether you are an international student. You need to select Yes or No on the screen.\n\n"+
                "What make UQFact awesome is the self training functionality:\n"+
                "If UQFact doesn't know the answer, you can help train it by clicking yes under that message and then type in or speak out the answer. (In the training mode you must click the Go button to submit your answer since voice recognition may have some slight problem)\n"+
                "Next time when someone else ask the same question, UQFact will answer it using your knowledge.\n\n"+
                "If you have any questions or any requirements, feel free to leave us a comment in the feedback page, the app will keep improving!";
        userGuide.setText(userGuideText);

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
}
