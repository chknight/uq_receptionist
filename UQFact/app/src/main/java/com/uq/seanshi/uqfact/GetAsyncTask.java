package com.uq.seanshi.uqfact;

import android.os.AsyncTask;

import com.google.gson.JsonObject;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.DataOutputStream;
import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.util.Map;

/**
 * Created by seanshi on 14/5/17.
 */

public class GetAsyncTask extends AsyncTask<Void, Void, String> {

    private final String USER_AGENT = "Mozilla/5.0";

    public GetAsyncTask() {

    }

    @Override
    protected String doInBackground(Void... params) {

        try {
            URL url = new URL("http://104.131.35.172:8888/"); //Enter URL here
            HttpURLConnection httpURLConnection = (HttpURLConnection) url.openConnection();
            httpURLConnection.setDoOutput(false);
            httpURLConnection.setRequestMethod("GET"); // here you are telling that it is a POST request, which can be changed into "PUT", "GET", "DELETE" etc.
            httpURLConnection.setRequestProperty("User-Agent", USER_AGENT);
            httpURLConnection.connect();

            int responseCode = httpURLConnection.getResponseCode();
            if (responseCode == HttpURLConnection.HTTP_OK) {
                return "Success";
            }

        } catch (MalformedURLException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }

        return "False";
    }

}
