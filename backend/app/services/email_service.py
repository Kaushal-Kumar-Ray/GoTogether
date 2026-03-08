import os
import resend

resend.api_key = os.environ.get("RESEND_API_KEY")


def send_email(receiver_email, otp):

    try:
        resend.Emails.send({
            "from": "GoTogether <onboarding@resend.dev>",
            "to": receiver_email,
            "subject": "GoTogether OTP Verification",
            "html": f"""
                <h2>GoTogether Verification Code</h2>
                <p>Your OTP is:</p>
                <h1>{otp}</h1>
                <p>This code expires in 5 minutes.</p>
            """
        })

    except Exception as e:
        print("Email error:", e)
        