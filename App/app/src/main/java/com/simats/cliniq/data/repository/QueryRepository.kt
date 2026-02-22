package com.simats.cliniq.data.repository

import android.content.Context
import com.simats.cliniq.data.api.RetrofitClient
import com.simats.cliniq.data.models.*

class QueryRepository(context: Context) {
    private val api = RetrofitClient.getApiService(context)

    suspend fun createQuery(queryText: String, urgency: String): Result<QueryResponse> {
        return try {
            val response = api.createQuery(QueryCreateRequest(queryText, urgency))
            if (response.isSuccessful) Result.success(response.body()!!)
            else Result.failure(Exception(response.errorBody()?.string() ?: "Failed to send query"))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getMyQueries(): Result<List<QueryResponse>> {
        return try {
            val response = api.getMyQueries()
            if (response.isSuccessful) Result.success(response.body()!!)
            else Result.failure(Exception("Failed to get queries"))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun respondToQuery(queryId: Int, responseText: String): Result<QueryResponse> {
        return try {
            val response = api.respondToQuery(queryId, QueryRespondRequest(responseText))
            if (response.isSuccessful) Result.success(response.body()!!)
            else Result.failure(Exception(response.errorBody()?.string() ?: "Failed to respond"))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getPendingCount(): Result<PendingCountResponse> {
        return try {
            val response = api.getPendingQueryCount()
            if (response.isSuccessful) Result.success(response.body()!!)
            else Result.failure(Exception("Failed to get count"))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getPendingQueries(): Result<List<QueryResponse>> {
        return try {
            val response = api.getPendingQueries()
            if (response.isSuccessful) Result.success(response.body()!!)
            else Result.failure(Exception("Failed to get pending queries"))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
