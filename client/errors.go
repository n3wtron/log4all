package client

type ErrorType struct {
	Description string
}

var (
	ERR_URL_MANDATORY         ErrorType = ErrorType{"Url is mandatory"}
	ERR_APPLICATION_MANDATORY ErrorType = ErrorType{"Application is mandatory"}
	ERR_ADD_LOG               ErrorType = ErrorType{"Error adding log"}
)

var errorMessages = []string{"Url is mandatory", "Application is mandatory", ""}

type ClientError struct {
	error
	ErrorType ErrorType
	Message   string
}

func NewClientError(errType ErrorType, message ...string) ClientError {
	var err ClientError
	err.ErrorType = errType
	if len(message) == 1 {
		err.Message = message[0]
	}
	return err
}

func (err ClientError) Error() string {
	if len(err.Message) > 0 {
		return err.ErrorType.Description + ":" + err.Message
	} else {
		return err.ErrorType.Description
	}
}
