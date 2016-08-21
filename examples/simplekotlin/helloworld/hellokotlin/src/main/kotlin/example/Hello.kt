package upload

import com.amazonaws.services.lambda.runtime.Context

class Upload {
    class EventClass {
        lateinit var key1: String
        lateinit var key2: String
        lateinit var key3: String

        constructor(key1: String, key2: String, key3: String) {
            this.key1 = key1
            this.key2 = key2
            this.key3 = key3
        }

        constructor() {
        }
    }

    fun handler(event: EventClass, context: Context): String {
        println("value1 = ${event.key1}")
        println("value2 = ${event.key2}")
        println("value3 = ${event.key3}")
        return "${event.key1}"
    }
}