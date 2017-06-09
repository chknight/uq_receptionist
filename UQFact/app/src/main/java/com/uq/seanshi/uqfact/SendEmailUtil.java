package com.uq.seanshi.uqfact;

import android.app.ProgressDialog;
import android.content.Context;
import android.os.AsyncTask;
import android.widget.Toast;

import java.util.Properties;
import javax.mail.Message;
import javax.mail.PasswordAuthentication;
import javax.mail.Session;
import javax.mail.Transport;
import javax.mail.internet.InternetAddress;
import javax.mail.internet.MimeMessage;

public class SendEmailUtil extends AsyncTask<Object, Object, String> {

    private String userEmail;
    private String userFeedback;
    private Context context;
    private ProgressDialog progDailog;

    SendEmailUtil(String userEmail, String userFeedback, Context context) {
        this.userEmail = userEmail;
        this.userFeedback = userFeedback;
        this.context = context;
    }
    @Override
    protected void onPreExecute() {
        super.onPreExecute();
        progDailog = new ProgressDialog(context);
        progDailog.setMessage("Sending Feedback...");
        progDailog.setProgressStyle(ProgressDialog.STYLE_SPINNER);
        progDailog.setCancelable(true);
        progDailog.show();
    }

    @Override
    protected String doInBackground(Object... params) {
        Properties props = new Properties();
        props.put("mail.smtp.host", "smtp.gmail.com");
        props.put("mail.smtp.socketFactory.port", "465");
        props.put("mail.smtp.socketFactory.class",
                "javax.net.ssl.SSLSocketFactory");
        props.put("mail.smtp.auth", "true");
        props.put("mail.smtp.port", "465");

        Session session = Session.getDefaultInstance(props,
                new javax.mail.Authenticator() {
                    protected PasswordAuthentication getPasswordAuthentication() {
                        return new PasswordAuthentication("uqfact","uqfactisgreat");
                    }
                });

        try {
            //send to myself
            Message message = new MimeMessage(session);
            message.setFrom(new InternetAddress("uqfact@gmail.com"));
            message.setRecipients(Message.RecipientType.TO,
                    InternetAddress.parse("uqfact@gmail.com"));
            message.setSubject("UQFact Feedback from " + userEmail);
            message.setText(userFeedback);

            //send to user
            Message messageUser = new MimeMessage(session);
            messageUser.setFrom(new InternetAddress("uqfact@gmail.com"));
            messageUser.setRecipients(Message.RecipientType.TO,
                    InternetAddress.parse(userEmail));
            messageUser.setSubject("UQFact: Thanks for your feedback");
            messageUser.setText("Thank you very much for your valuable opinion, we'll get back to you soon!");

            Transport.send(messageUser);
            Transport.send(message);

            System.out.println("Done");

            return "Done";

        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }

    @Override
    protected void onPostExecute(String str) {
        progDailog.dismiss();
        if (str.equals("Done")) {
            Toast toast = Toast.makeText(context, "We've received your feedback!", Toast.LENGTH_LONG);
            toast.show();
        }
    }

}