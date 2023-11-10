runtime_exception_prompt =  """
try to explain what's the issue to a non-techinical guy in few words In Chinese.
Accroding the exception information,give the possible advice to try to fix  the issue.

---
The runtime exception's stack is as follows: 
{runtime_exception_stack}
"""