package com.simats.cliniq.ui.auth

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.viewModelScope
import com.simats.cliniq.data.models.TokenResponse
import com.simats.cliniq.data.models.UserResponse
import com.simats.cliniq.data.repository.AuthRepository
import kotlinx.coroutines.launch

class AuthViewModel(application: Application) : AndroidViewModel(application) {

    private val repository = AuthRepository(application)

    private val _loginResult = MutableLiveData<Result<TokenResponse>>()
    val loginResult: LiveData<Result<TokenResponse>> = _loginResult

    private val _signupResult = MutableLiveData<Result<UserResponse>>()
    val signupResult: LiveData<Result<UserResponse>> = _signupResult

    private val _isLoading = MutableLiveData(false)
    val isLoading: LiveData<Boolean> = _isLoading

    fun login(email: String, password: String) {
        _isLoading.value = true
        viewModelScope.launch {
            val result = repository.login(email, password)
            _loginResult.value = result
            _isLoading.value = false
        }
    }

    fun signup(email: String, username: String, password: String, fullName: String?, role: String) {
        _isLoading.value = true
        viewModelScope.launch {
            val result = repository.signup(email, username, password, fullName, role)
            _signupResult.value = result
            _isLoading.value = false
        }
    }

    fun isLoggedIn() = repository.isLoggedIn()
    fun getUserRole() = repository.getUserRole()
}
