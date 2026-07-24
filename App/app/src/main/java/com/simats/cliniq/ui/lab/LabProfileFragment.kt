package com.simats.cliniq.ui.lab

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import com.simats.cliniq.data.local.SessionManager
import com.simats.cliniq.databinding.FragmentLabProfileBinding

class LabProfileFragment : Fragment() {

    private var _binding: FragmentLabProfileBinding? = null
    private val binding get() = _binding!!

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        _binding = FragmentLabProfileBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val user = SessionManager.getInstance(requireContext()).getUser()
        binding.tvName.text = user?.fullName ?: user?.username ?: "Lab"
        binding.tvEmail.text = user?.email ?: ""
        binding.tvUsername.text = "Username: ${user?.username}"
        binding.tvRole.text = "Role: Lab"
        binding.tvAccountCreated.text = "Member since: ${user?.createdAt?.substringBefore("T") ?: "N/A"}"
    }

    override fun onDestroyView() { super.onDestroyView(); _binding = null }
}
