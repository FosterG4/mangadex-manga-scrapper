# MangaDx API Rate Limits

This document explains the rate limits enforced by MangaDx API and how the Mangadx scrapper application handles them.

## Official Rate Limits

According to [MangaDx API Documentation](https://api.mangadex.org/docs/2-limitations/):

### Global Rate Limit
- **~5 requests per second per IP address**
- This is a minimum guaranteed allowance
- Enforced at load balancer level

### Consequences of Exceeding Limits

1. **First violation**: HTTP 429 (Too Many Requests)
   - All requests to `*.mangadex.org` will return 429
   - Must wait until rate comes back in line

2. **Persistent violations**: Temporary IP ban
   - DDoS protection triggers automatically
   - HTTP 403 (Forbidden) for all requests
   - Duration is undocumented and subject to change

3. **Continued violations**: Complete block
   - API stops responding to your IP entirely
   - Cooldown period renewed for every request sent
   - Duration is undocumented and subject to change

### Additional Requirements

- **User-Agent header**: MUST be present and not spoofed
- **No Via header**: Non-transparent proxies not allowed
- **TLS required**: All requests must use HTTPS

## Application Configuration

### Default Settings

```bash
# Rate Limiting (configured in .env)
RATE_LIMIT_DELAY=0.25    # 0.25 seconds = 4 requests/second (safe margin)
MAX_RETRIES=3            # Number of retry attempts
RETRY_DELAY=2.0          # Delay between retries
```

### Why 0.25 seconds?

- MangaDex allows ~5 req/s
- We use 4 req/s (0.25s delay) to stay safely below the limit
- Provides buffer for network latency and timing variations
- Prevents accidental rate limit violations

### Additional Protections

1. **Between API calls**: `RATE_LIMIT_DELAY` (0.25s default)
2. **Between chapters**: `RATE_LIMIT_DELAY * 2` (0.5s default)
3. **On HTTP 429**: Automatic retry with exponential backoff
4. **On errors**: Configurable retry delay

## Best Practices

### ✅ DO

- **Use default settings**: They're configured to be safe
- **Monitor for 429 errors**: Check logs if downloads fail
- **Respect retry-after headers**: Application handles this automatically
- **Use reasonable concurrent downloads**: Default is 10 workers
- **Add delays between large operations**: Built into the application

### ❌ DON'T

- **Set RATE_LIMIT_DELAY below 0.2**: Risk of hitting rate limits
- **Disable rate limiting**: Will result in IP ban
- **Make parallel requests to API**: Use the built-in client
- **Ignore 429 responses**: Application retries automatically
- **Run multiple instances**: Shares same IP rate limit

## Adjusting Rate Limits

### For Slower Connections

If you experience timeouts or connection issues:

```bash
# Increase delays
RATE_LIMIT_DELAY=0.5     # Slower but more reliable
MAX_CONCURRENT_DOWNLOADS=5  # Fewer parallel downloads
```

### For Faster Connections

**NOT RECOMMENDED** - Risk of IP ban. Only if you understand the risks:

```bash
# Minimum safe values
RATE_LIMIT_DELAY=0.2     # 5 req/s (at the limit)
MAX_CONCURRENT_DOWNLOADS=10
```

## Monitoring Rate Limits

### Check Response Headers

The application logs rate limit information from these headers:

- `X-RateLimit-Limit`: Your rate limit
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Retry-After`: Seconds to wait

### Log Messages

Watch for these in logs:

```
[WARNING] Rate limit exceeded, retrying after X seconds
[ERROR] Rate limited: Retry after X seconds
```

## Troubleshooting

### Getting HTTP 429 Errors

1. **Increase RATE_LIMIT_DELAY**:
   ```bash
   RATE_LIMIT_DELAY=0.5
   ```

2. **Reduce concurrent downloads**:
   ```bash
   MAX_CONCURRENT_DOWNLOADS=5
   ```

3. **Wait before retrying**: Give your IP time to cool down

### Getting HTTP 403 Errors

This means you've been temporarily banned:

1. **Stop all requests immediately**
2. **Wait at least 15-30 minutes**
3. **Review your rate limit settings**
4. **Increase delays significantly**:
   ```bash
   RATE_LIMIT_DELAY=1.0
   ```

### Complete IP Block

If API stops responding:

1. **Stop all requests for several hours**
2. **Check if you're running multiple instances**
3. **Verify no other applications are using MangaDex API**
4. **Contact MangaDex if block persists after 24 hours**

## Endpoint-Specific Limits

Some endpoints have additional restrictions:

- `GET /at-home/server/{id}`: Used for getting chapter images
- `GET /manga/random`: Rate limited
- POST/PUT/DELETE operations: Heavily rate limited

The application handles these automatically with appropriate delays.

## Technical Implementation

### HTTP Client

The `HTTPClient` class implements:

- Automatic rate limiting between requests
- Retry logic with exponential backoff
- Rate limit header parsing
- 429 response handling

### Download Manager

The `DownloadManager` adds:

- Extra delays between chapters
- Concurrent download limiting
- Progress tracking without overwhelming API
- Automatic resume on rate limit errors

## Summary

**Default configuration is safe and recommended.**

- ✅ 4 requests/second (0.25s delay)
- ✅ Extra delays between chapters
- ✅ Automatic retry on rate limits
- ✅ Respects retry-after headers
- ✅ Proper User-Agent header

**Only adjust if you experience issues, and always increase delays rather than decrease them.**

## References

- [MangaDex API Limitations](https://api.mangadex.org/docs/2-limitations/)
- [MangaDex API Documentation](https://api.mangadex.org/docs/)
- [HTTP 429 Status Code](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/429)
