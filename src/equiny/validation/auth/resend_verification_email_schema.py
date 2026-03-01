from equiny.validation.shared import EmailSchema, Schema


class ResendVerificationEmailSchema(Schema):
    account_email: EmailSchema
