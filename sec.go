package tmdb

import (
	"context"
	"net/http"
)

// WithToken authenticates the client's requests with a Bearer token.
func WithToken(token string) ClientOption {
	return WithRequestEditorFn(func(_ context.Context, req *http.Request) error {
		req.Header.Set("Authorization", "Bearer "+token)
		return nil
	})
}
