package com.simats.cliniq.ui.doctor

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import androidx.recyclerview.widget.LinearLayoutManager
import com.simats.cliniq.R
import com.simats.cliniq.databinding.FragmentDoctorPatientsBinding
import com.simats.cliniq.ui.common.PatientAdapter

class DoctorPatientsFragment : Fragment() {

    private var _binding: FragmentDoctorPatientsBinding? = null
    private val binding get() = _binding!!
    private val viewModel: DoctorViewModel by activityViewModels()

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        _binding = FragmentDoctorPatientsBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        binding.rvPatients.layoutManager = LinearLayoutManager(requireContext())

        binding.swipeRefresh.setOnRefreshListener { viewModel.loadPatients() }

        viewModel.patients.observe(viewLifecycleOwner) { result ->
            binding.swipeRefresh.isRefreshing = false
            result.onSuccess { data ->
                binding.tvPatientCount.text = "${data.patientCount} patients linked to you"
                if (data.patients.isEmpty()) {
                    binding.tvNoPatients.visibility = View.VISIBLE
                    binding.rvPatients.visibility = View.GONE
                } else {
                    binding.tvNoPatients.visibility = View.GONE
                    binding.rvPatients.visibility = View.VISIBLE
                    binding.rvPatients.adapter = PatientAdapter(data.patients) { patient ->
                        parentFragmentManager.beginTransaction()
                            .replace(
                                R.id.fragment_container,
                                PatientDetailFragment.newInstance(
                                    patient.id,
                                    patient.fullName ?: patient.username,
                                    patient.email,
                                    patient.createdAt
                                )
                            )
                            .addToBackStack("patient_detail")
                            .commit()
                    }
                }
            }
            result.onFailure {
                binding.tvNoPatients.visibility = View.VISIBLE
                binding.rvPatients.visibility = View.GONE
                binding.tvPatientCount.text = "Could not load patients"
            }
        }

        viewModel.loadPatients()
    }

    override fun onDestroyView() { super.onDestroyView(); _binding = null }
}
