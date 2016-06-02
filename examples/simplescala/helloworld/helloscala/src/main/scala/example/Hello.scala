package example

import com.amazonaws.services.lambda.runtime.Context

class Hello {
  def handler(context: Context): Unit = {
      println(s"Hello World")
  }
}