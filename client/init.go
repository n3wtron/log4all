package client

type Client struct {
	Url              string
	Application      string
	ApplicationToken string
}

func NewClient(url, application, applicationToken string) (*Client, error) {
	cl := new(Client)
	if len(url) == 0 {
		return nil, NewClientError(ERR_URL_MANDATORY)
	}
	cl.Application = application
	cl.ApplicationToken = applicationToken
	cl.Url = url
	return cl, nil
}
