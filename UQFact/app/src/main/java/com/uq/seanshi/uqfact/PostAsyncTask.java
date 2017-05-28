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

public class PostAsyncTask extends AsyncTask<Void, Void, String> {

    private Map<String, String> map;

    public PostAsyncTask(Map<String, String> map) {
        this.map = map;
    }

    @Override
    protected String doInBackground(Void... params) {

        try {
            URL url = new URL("http://104.131.35.172:8888/" + map.get("url")); //Enter URL here
            HttpURLConnection httpURLConnection = (HttpURLConnection) url.openConnection();
            httpURLConnection.setDoOutput(true);
            httpURLConnection.setRequestMethod("POST"); // here you are telling that it is a POST request, which can be changed into "PUT", "GET", "DELETE" etc.
            httpURLConnection.setRequestProperty("Content-Type", "application/json"); // here you are setting the `Content-Type` for the data you are sending which is `application/json`
            httpURLConnection.connect();

            JSONObject jsonObject = new JSONObject();
            for (String obj : map.keySet()) {
                if (!obj.equals("url")) {
                    jsonObject.put(obj, map.get(obj));
                }
            }

            DataOutputStream wr = new DataOutputStream(httpURLConnection.getOutputStream());
            wr.writeBytes(jsonObject.toString());
            wr.flush();
            int responseCode = httpURLConnection.getResponseCode();
            if (responseCode == HttpURLConnection.HTTP_OK) {
                wr.close();
                return "Success";
            }

        } catch (MalformedURLException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        } catch (JSONException e) {
            e.printStackTrace();
        }

        return null;
    }

}
