package com.uq.seanshi.uqfact;

/**
 * Created by seanshi on 9/5/17.
 */

public class ChatMessage {
    public boolean left;
    public boolean wantTrain;
    public boolean wantNationality;
    public String message;

    public ChatMessage(boolean left, String message) {
        super();
        this.left = left;
        this.wantTrain = false;
        this.wantNationality = false;
        this.message = message;
    }

    public ChatMessage(boolean left, boolean wantTrain, String message) {
        super();
        this.left = left;
        this.wantTrain = wantTrain;
        this.wantNationality =false;
        this.message = message;
    }

    public ChatMessage(boolean left, boolean wantTrain, boolean wantNationality, String message) {
        super();
        this.left = left;
        this.wantTrain = wantTrain;
        this.wantNationality = wantNationality;
        this.message = message;
    }
}
