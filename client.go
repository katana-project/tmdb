package tmdb

import (
	"context"
	"net/http"
)

// DefaultServerBaseURL is the default TMDB API base URL.
const DefaultServerBaseURL = "https://api.themoviedb.org/"

// NewDefaultClient creates a new Client with the DefaultServerBaseURL base URL and a WithToken ClientOption.
func NewDefaultClient(token string, opts ...ClientOption) (*Client, error) {
	return NewClient(DefaultServerBaseURL, append(opts, WithToken(token))...)
}

// WithToken authenticates the client's requests with a Bearer token.
func WithToken(token string) ClientOption {
	return WithRequestEditorFn(func(_ context.Context, req *http.Request) error {
		req.Header.Set("Authorization", "Bearer "+token)
		return nil
	})
}

// Response is an abstraction of a typed http.Response wrapper.
type Response interface {
	// Status returns the status text.
	Status() string
	// StatusCode returns the status code.
	StatusCode() int
}
