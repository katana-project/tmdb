// Code generated by ogen, DO NOT EDIT.

package tmdb

import (
	"context"
	"net/http"

	"github.com/go-faster/errors"
)

// SecuritySource is provider of security values (tokens, passwords, etc.).
type SecuritySource interface {
	// Sec0 provides sec0 security value.
	Sec0(ctx context.Context, operationName string) (Sec0, error)
}

func (s *Client) securitySec0(ctx context.Context, operationName string, req *http.Request) error {
	t, err := s.sec.Sec0(ctx, operationName)
	if err != nil {
		return errors.Wrap(err, "security source \"Sec0\"")
	}
	req.Header.Set("Authorization", t.APIKey)
	return nil
}
