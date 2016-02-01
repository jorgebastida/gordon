package example;

import com.amazonaws.services.lambda.runtime.Context;

public class Hello {

    public static class EventClass {
        String key1;

        public String getKey1() {
            return key1;
        }

        public void setKey1(String key1) {
            this.key1 = key1;
        }

        public EventClass(String key1) {
            this.key1 = key1;
        }

        public EventClass() {}
    }

    public String handler(EventClass event, Context context) {
        return String.format(event.key1);
    }

}
