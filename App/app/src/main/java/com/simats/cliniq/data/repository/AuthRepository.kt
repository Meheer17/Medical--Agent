package com.simats.cliniq.data.repository

import android.content.Context
import com.simats.cliniq.data.api.RetrofitClient
import com.simats.cliniq.data.local.SessionManager
import com.simats.cliniq.data.models.*

class AuthRepository(context: Context) {
    private val api = RetrofitClient.getApiService(context)
    private val session = SessionManager.getInstance(context)

    suspend fun login(email: String, password: String): Result<TokenResponse> {
        return try {
            val response = api.login(LoginRequest(email, password))
            if (response.isSuccessful) {
                val body = response.body()!!
                session.saveAuthToken(body.accessToken)
                session.saveUser(body.user)
                Result.success(body)
            } else {
                val error = response.errorBody()?.string() ?: "Login failed"
                Result.failure(Exception(error))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun signup(
        email: String, username: String, password: String,
        fullName: String?, role: String
    ): Result<UserResponse> {
        return try {
            val response = api.signup(SignupRequest(email, username, password, fullName, role))
            if (response.isSuccessful) {
                Result.success(response.body()!!)
            } else {
                val error = response.errorBody()?.string() ?: "Signup failed"
                Result.failure(Exception(error))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getCurrentUser(): Result<UserResponse> {
        return try {
            val response = api.getCurrentUser()
            if (response.isSuccessful) {
                val user = response.body()!!
                session.saveUser(user)
                Result.success(user)
            } else {
                Result.failure(Exception("Failed to get user"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    fun logout() {
        session.logout()
        RetrofitClient.resetClient()
    }

    fun isLoggedIn() = session.isLoggedIn()
    fun getUser() = session.getUser()
    fun getUserRole() = session.getUserRole()
}
