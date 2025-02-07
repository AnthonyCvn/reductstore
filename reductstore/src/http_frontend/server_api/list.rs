// Copyright 2023 ReductStore
// This Source Code Form is subject to the terms of the Mozilla Public
//    License, v. 2.0. If a copy of the MPL was not distributed with this
//    file, You can obtain one at https://mozilla.org/MPL/2.0/.

use crate::auth::policy::AuthenticatedPolicy;
use crate::http_frontend::middleware::check_permissions;
use crate::http_frontend::server_api::BucketInfoListAxum;
use crate::http_frontend::{HttpError, HttpServerState};
use axum::extract::State;
use axum::headers::HeaderMap;
use std::sync::Arc;

// GET /list
pub async fn list(
    State(components): State<Arc<HttpServerState>>,
    headers: HeaderMap,
) -> Result<BucketInfoListAxum, HttpError> {
    check_permissions(&components, headers, AuthenticatedPolicy {}).await?;

    let list = components.storage.read().await.get_bucket_list()?;
    Ok(BucketInfoListAxum::from(list))
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::http_frontend::tests::{components, headers};
    use rstest::rstest;

    #[rstest]
    #[tokio::test]
    async fn test_list(components: Arc<HttpServerState>, headers: HeaderMap) {
        let list = list(State(components), headers).await.unwrap();
        assert_eq!(list.0.buckets.len(), 2);
    }
}
