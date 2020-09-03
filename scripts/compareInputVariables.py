#!/usr/bin/env python

import json

from TauMLTools.Training.common import *

reporting_threshold = 1.e-3

inputFileName_hdf5  = "/home/veelken/Phase2HLT_DeepTau/CMSSW_11_1_0/src/HLTrigger/DeepTauTraining/test/apply_training_0.json"
inputFileName_cmssw = "/home/veelken/Phase2HLT_DeepTau/CMSSW_11_1_0/src/HLTrigger/DeepTauTraining/test/DeepTauId_0.json"

inputVariableNames_tau_hdf5 = input_event_branches + input_tau_branches
inputVariableNames_egamma_hdf5 = input_cell_external_branches + input_cell_pfCand_ele_branches + input_cell_ele_branches + input_cell_pfCand_gamma_branches
inputVariableNames_muon_hdf5 = input_cell_external_branches + input_cell_pfCand_muon_branches + input_cell_muon_branches
inputVariableNames_hadrons_hdf5 = input_cell_external_branches + input_cell_pfCand_chHad_branches + input_cell_pfCand_nHad_branches

print("hdf5:")
print("#tau inputs = %i" % len(inputVariableNames_tau_hdf5))
print("#e/gamma inputs = %i" % len(inputVariableNames_egamma_hdf5))
print("#muon inputs = %i" % len(inputVariableNames_muon_hdf5))
print("#hadron inputs = %i" % len(inputVariableNames_hadrons_hdf5))
print("")

#------------------------------------------------------------------------------------------------------------------------
# CV: list of CMSSW input variables taken from the enums defined in RecoTauTag/RecoTau/plugins/DeepTauId.cc
inputVariableNames_tau_cmssw = [  
  'rho', 'tau_pt', 'tau_eta', 'tau_phi', 'tau_mass', 'tau_E_over_pt', 'tau_charge',
  'tau_n_charged_prongs', 'tau_n_neutral_prongs', 'chargedIsoPtSumHGCalFix',
  'chargedIsoPtSumdR03_over_dR05HGCalFix', 'footprintCorrection', 'neutralIsoPtSumHGCalFix',
  'neutralIsoPtSumWeight_over_neutralIsoPtSum', 'neutralIsoPtSumWeightdR03_over_neutralIsoPtSum',
  'neutralIsoPtSumdR03_over_dR05HGCalFix', 'photonPtSumOutsideSignalCone', 'puCorrPtSum',
  'tau_dxy_valid', 'tau_dxy', 'tau_dxy_sig', 
  'tau_ip3d_valid', 'tau_ip3d', 'tau_ip3d_sig', 'tau_dz', 'tau_dz_sig_valid', 'tau_dz_sig',
  'tau_flightLength_x', 'tau_flightLength_y', 'tau_flightLength_z', 'tau_flightLength_sig',
  'tau_pt_weighted_deta_strip', 'tau_pt_weighted_dphi_strip', 'tau_pt_weighted_dr_signal',
  'tau_pt_weighted_dr_iso', 'tau_leadingTrackNormChi2', 'tau_e_ratio_valid', 'tau_e_ratio',
  'tau_gj_angle_diff_valid', 'tau_gj_angle_diff', 'tau_n_photons', 'tau_emFraction', 
  'tau_inside_ecal_crack', 'leadChargedCand_etaAtEcalEntrance_minus_tau_eta'
]

inputVariableNames_egamma_cmssw = [
  'rho', 'tau_pt', 'tau_eta', 'tau_inside_ecal_crack',
  'pfCand_ele_valid', 'pfCand_ele_rel_pt', 'pfCand_ele_deta', 'pfCand_ele_dphi',
  'pfCand_ele_pvAssociationQuality', 'pfCand_ele_puppiWeight', 'pfCand_ele_charge',
  'pfCand_ele_lostInnerHits', 'pfCand_ele_numberOfPixelHits', 'pfCand_ele_vertex_dx',
  'pfCand_ele_vertex_dy', 'pfCand_ele_vertex_dz', 'pfCand_ele_vertex_dx_tauFL',
  'pfCand_ele_vertex_dy_tauFL', 'pfCand_ele_vertex_dz_tauFL',
  'pfCand_ele_hasTrackDetails', 'pfCand_ele_dxy', 'pfCand_ele_dxy_sig',
  'pfCand_ele_dz', 'pfCand_ele_dz_sig', 'pfCand_ele_track_chi2_ndof', 
  'pfCand_ele_track_ndof',
  'ele_valid', 'ele_rel_pt', 'ele_deta', 'ele_dphi', 'ele_cc_valid', 'ele_cc_ele_rel_energy',
  'ele_cc_gamma_rel_energy', 'ele_cc_n_gamma', 'ele_rel_trackMomentumAtVtx',
  'ele_rel_trackMomentumAtCalo', 'ele_rel_trackMomentumOut',
  'ele_rel_trackMomentumAtEleClus', 'ele_rel_trackMomentumAtVtxWithConstraint',
  'ele_rel_ecalEnergy', 'ele_ecalEnergy_sig', 'ele_eSuperClusterOverP',
  'ele_eSeedClusterOverP', 'ele_eSeedClusterOverPout', 'ele_eEleClusterOverPout',
  'ele_deltaEtaSuperClusterTrackAtVtx', 'ele_deltaEtaSeedClusterTrackAtCalo',
  'ele_deltaEtaEleClusterTrackAtCalo', 'ele_deltaPhiEleClusterTrackAtCalo',
  'ele_deltaPhiSuperClusterTrackAtVtx', 'ele_deltaPhiSeedClusterTrackAtCalo',
  'ele_mvaInput_earlyBrem', 'ele_mvaInput_lateBrem', 'ele_mvaInput_sigmaEtaEta',
  'ele_mvaInput_hadEnergy', 'ele_mvaInput_deltaEta', 'ele_gsfTrack_normalizedChi2',
  'ele_gsfTrack_numberOfValidHits', 'ele_rel_gsfTrack_pt', 'ele_gsfTrack_pt_sig',
  'ele_has_closestCtfTrack', 'ele_closestCtfTrack_normalizedChi2',
  'ele_closestCtfTrack_numberOfValidHits',
  'pfCand_gamma_valid', 'pfCand_gamma_rel_pt', 'pfCand_gamma_deta',
  'pfCand_gamma_dphi', 'pfCand_gamma_pvAssociationQuality', 'pfCand_gamma_fromPV',
  'pfCand_gamma_puppiWeight', 'pfCand_gamma_puppiWeightNoLep',
  'pfCand_gamma_lostInnerHits', 'pfCand_gamma_numberOfPixelHits',
  'pfCand_gamma_vertex_dx', 'pfCand_gamma_vertex_dy', 'pfCand_gamma_vertex_dz',
  'pfCand_gamma_vertex_dx_tauFL', 'pfCand_gamma_vertex_dy_tauFL',
  'pfCand_gamma_vertex_dz_tauFL', 'pfCand_gamma_hasTrackDetails',
  'pfCand_gamma_dxy', 'pfCand_gamma_dxy_sig', 'pfCand_gamma_dz',
  'pfCand_gamma_dz_sig', 'pfCand_gamma_track_chi2_ndof', 'pfCand_gamma_track_ndof'
]

inputVariableNames_muon_cmssw = [
  'rho', 'tau_pt', 'tau_eta', 'tau_inside_ecal_crack',
  'pfCand_muon_valid', 'pfCand_muon_rel_pt', 'pfCand_muon_deta', 'pfCand_muon_dphi',
  'pfCand_muon_pvAssociationQuality', 'pfCand_muon_fromPV',
  'pfCand_muon_puppiWeight', 'pfCand_muon_charge', 'pfCand_muon_lostInnerHits',
  'pfCand_muon_numberOfPixelHits', 'pfCand_muon_vertex_dx', 'pfCand_muon_vertex_dy',
  'pfCand_muon_vertex_dz', 'pfCand_muon_vertex_dx_tauFL',
  'pfCand_muon_vertex_dy_tauFL', 'pfCand_muon_vertex_dz_tauFL',
  'pfCand_muon_hasTrackDetails', 'pfCand_muon_dxy', 'pfCand_muon_dxy_sig',
  'pfCand_muon_dz', 'pfCand_muon_dz_sig', 'pfCand_muon_track_chi2_ndof',
  'pfCand_muon_track_ndof',
  'muon_valid', 'muon_rel_pt', 'muon_deta', 'muon_dphi', 'muon_dxy', 'muon_dxy_sig',
  'muon_normalizedChi2_valid', 'muon_normalizedChi2', 'muon_numberOfValidHits',
  'muon_segmentCompatibility', 'muon_caloCompatibility', 'muon_pfEcalEnergy_valid',
  'muon_rel_pfEcalEnergy', 'muon_n_matches_DT_1', 'muon_n_matches_DT_2',
  'muon_n_matches_DT_3', 'muon_n_matches_DT_4', 'muon_n_matches_CSC_1',
  'muon_n_matches_CSC_2', 'muon_n_matches_CSC_3', 'muon_n_matches_CSC_4',
  'muon_n_matches_RPC_1', 'muon_n_matches_RPC_2', 'muon_n_matches_RPC_3',
  'muon_n_matches_RPC_4', 'muon_n_hits_DT_1', 'muon_n_hits_DT_2', 'muon_n_hits_DT_3',
  'muon_n_hits_DT_4', 'muon_n_hits_CSC_1', 'muon_n_hits_CSC_2', 'muon_n_hits_CSC_3',
  'muon_n_hits_CSC_4', 'muon_n_hits_RPC_1', 'muon_n_hits_RPC_2', 'muon_n_hits_RPC_3',
  'muon_n_hits_RPC_4'
]

inputVariableNames_hadrons_cmssw = [
  'rho', 'tau_pt', 'tau_eta', 'tau_inside_ecal_crack',
  'pfCand_chHad_valid', 'pfCand_chHad_rel_pt', 'pfCand_chHad_deta',
  'pfCand_chHad_dphi', 'pfCand_chHad_leadChargedHadrCand',
  'pfCand_chHad_pvAssociationQuality', 'pfCand_chHad_fromPV',
  'pfCand_chHad_puppiWeight', 'pfCand_chHad_puppiWeightNoLep',
  'pfCand_chHad_charge', 'pfCand_chHad_lostInnerHits',
  'pfCand_chHad_numberOfPixelHits', 'pfCand_chHad_vertex_dx',
  'pfCand_chHad_vertex_dy', 'pfCand_chHad_vertex_dz',
  'pfCand_chHad_vertex_dx_tauFL', 'pfCand_chHad_vertex_dy_tauFL',
  'pfCand_chHad_vertex_dz_tauFL', 'pfCand_chHad_hasTrackDetails',
  'pfCand_chHad_dxy', 'pfCand_chHad_dxy_sig', 'pfCand_chHad_dz',
  'pfCand_chHad_dz_sig', 'pfCand_chHad_track_chi2_ndof', 'pfCand_chHad_track_ndof',
  'pfCand_chHad_hcalFraction', 'pfCand_chHad_rawCaloFraction',
  'pfCand_nHad_valid', 'pfCand_nHad_rel_pt', 'pfCand_nHad_deta', 'pfCand_nHad_dphi',
  'pfCand_nHad_puppiWeight', 'pfCand_nHad_puppiWeightNoLep', 'pfCand_nHad_hcalFraction'
]
#------------------------------------------------------------------------------------------------------------------------

print("CMSSW:")
print("#tau inputs = %i" % len(inputVariableNames_tau_cmssw))
print("#e/gamma inputs = %i" % len(inputVariableNames_egamma_cmssw))
print("#muon inputs = %i" % len(inputVariableNames_muon_cmssw))
print("#hadron inputs = %i" % len(inputVariableNames_hadrons_cmssw))
print("")

inputFile_hdf5 = open(inputFileName_hdf5, "r") 
inputVariables_hdf5 = json.load(inputFile_hdf5)
inputFile_hdf5.close()

inputFile_cmssw = open(inputFileName_cmssw, "r") 
inputVariables_cmssw = json.load(inputFile_cmssw)
inputFile_cmssw.close()

def compVars(key, vars_hdf5, varNames_hdf5, vars_cmssw, varNames_cmssw):
    if len(varNames_hdf5) != len(varNames_cmssw):
        raise ValueError("Mismatch in number of input variables: hdf5 = %i, CMSSSW = %i" % (len(varNames_hdf5), len(varNames_cmssw)))
    if not key in vars_hdf5.keys():
        raise ValueError("Given key = '%s' not found in hdf5 input variables. Valid keys = %s" % (key, vars_hdf5.keys()))
    vars_hdf5 = vars_hdf5[key]
    if not key in vars_cmssw.keys():
        raise ValueError("Given key = '%s' not found in CMSSW input variables. Valid keys = %s" % (key, vars_cmssw.keys()))
    vars_cmssw = vars_cmssw[key]
    if len(vars_hdf5) != len(varNames_hdf5):
        raise ValueError("Array of hdf5 input variables has wrong dimension: expected = %i, got = %i" % (len(varNames_hdf5), len(vars_hdf5[key])))
    if len(vars_cmssw) != len(varNames_cmssw):
        raise ValueError("Array of CMSSW input variables has wrong dimension: expected = %i, got = %i" % (len(varNames_cmssw), len(vars_cmssw[key])))
    print("Checking %s:" % key)
    n_var = len(varNames_hdf5)
    for idx_var in range(n_var):
        var_hdf5 = vars_hdf5[idx_var]
        var_cmssw = vars_cmssw[idx_var]
        diff = abs(var_hdf5 - var_cmssw)
        mean = 0.5*(abs(var_hdf5) + abs(var_cmssw))
        if diff > (reporting_threshold*mean):
            label_hdf5 = "(%s)" % varNames_hdf5[idx_var]
            label_cmssw = "(%s)" % varNames_cmssw[idx_var]
            print("Mismatch in variable #%i: hdf5 %s = %1.4f, CMSSW %s = %1.4f" % (idx_var, label_hdf5, var_hdf5, label_cmssw, var_cmssw))
    print(" Done.")

compVars("input_tau", inputVariables_hdf5, inputVariableNames_tau_hdf5, inputVariables_cmssw, inputVariableNames_tau_cmssw)

def compVars_grid(key, vars_hdf5, varNames_hdf5, vars_cmssw, varNames_cmssw):
    if len(varNames_hdf5) != len(varNames_cmssw):
        raise ValueError("Mismatch in number of input variables: hdf5 = %i, CMSSSW = %i" % (len(varNames_hdf5), len(varNames_cmssw))) 
    if not key in vars_hdf5.keys():
        raise ValueError("Given key = '%s' not found in hdf5 input variables. Valid keys = %s" % (key, vars_hdf5.keys()))
    vars_hdf5 = vars_hdf5[key]
    if not key in vars_cmssw.keys():
        raise ValueError("Given key = '%s' not found in CMSSW input variables. Valid keys = %s" % (key, vars_cmssw.keys()))
    vars_cmssw = vars_cmssw[key]
    n_eta = None
    n_phi = None
    if key.find("input_inner") != -1:
        n_eta = 11
        n_phi = 11
    elif key.find("input_outer") != -1:
        n_eta = 21
        n_phi = 21
    else:
        raise ValueError("No eta-phi grid defined for key = '%s' !!" % key)
    if len(vars_hdf5) != n_eta:
        raise ValueError("Array of hdf5 input variables has wrong dimension: expected = %i, got = %i" % (n_eta, len(vars_hdf5)))
    if len(vars_cmssw) != n_eta:
        raise ValueError("Array of CMSSW input variables has wrong dimension: expected = %i, got = %i" % (n_eta, len(vars_cmssw)))
    print("Checking %s:" % key)
    n_var = len(varNames_hdf5)
    for idx_eta in range(n_eta):
        if len(vars_hdf5[idx_eta]) != n_phi:
            raise ValueError("Array of hdf5 input variables has wrong dimension: expected = %i, got = %i" % (n_phi, len(vars_hdf5[idx_eta])))
        if len(vars_cmssw[idx_eta]) != n_phi:
            raise ValueError("Array of CMSSW input variables has wrong dimension: expected = %i, got = %i" % (n_phi, len(vars_cmssw[idx_eta])))
        for idx_phi in range(n_phi):
            if len(vars_hdf5[idx_eta][idx_phi]) != len(varNames_hdf5):
                raise ValueError("Array of hdf5 input variables has wrong dimension: expected = %i, got = %i" % (len(varNames_hdf5), len(vars_hdf5[idx_eta][idx_phi])))
            if len(vars_cmssw[idx_eta][idx_phi]) != len(varNames_cmssw):
                raise ValueError("Array of CMSSW input variables has wrong dimension: expected = %i, got = %i" % (len(varNames_cmssw), len(vars_cmssw[idx_eta][idx_phi])))
            for idx_var in range(n_var):
                var_hdf5 = vars_hdf5[idx_eta][idx_phi][idx_var]
                var_cmssw = vars_cmssw[idx_eta][idx_phi][idx_var]
                diff = abs(var_hdf5 - var_cmssw)
                mean = 0.5*(abs(var_hdf5) + abs(var_cmssw))
                if diff > (reporting_threshold*mean):
                    label_hdf5 = "(%s)" % varNames_hdf5[idx_var]
                    label_cmssw = "(%s)" % varNames_cmssw[idx_var]
                    eta = idx_eta - n_eta/2
                    phi = idx_phi - n_phi/2
                    print("Mismatch in variable #%i @ (eta=%i, phi=%i): hdf5 %s = %1.4f, CMSSW %s = %1.4f" % (idx_var, eta, phi, label_hdf5, var_hdf5, label_cmssw, var_cmssw))
    print(" Done.")

compVars_grid("input_inner_egamma",  inputVariables_hdf5, inputVariableNames_egamma_hdf5,  inputVariables_cmssw, inputVariableNames_egamma_cmssw)
compVars_grid("input_inner_muon",    inputVariables_hdf5, inputVariableNames_muon_hdf5,    inputVariables_cmssw, inputVariableNames_muon_cmssw)
compVars_grid("input_inner_hadrons", inputVariables_hdf5, inputVariableNames_hadrons_hdf5, inputVariables_cmssw, inputVariableNames_hadrons_cmssw)

compVars_grid("input_outer_egamma",  inputVariables_hdf5, inputVariableNames_egamma_hdf5,  inputVariables_cmssw, inputVariableNames_egamma_cmssw)
compVars_grid("input_outer_muon",    inputVariables_hdf5, inputVariableNames_muon_hdf5,    inputVariables_cmssw, inputVariableNames_muon_cmssw)
compVars_grid("input_outer_hadrons", inputVariables_hdf5, inputVariableNames_hadrons_hdf5, inputVariables_cmssw, inputVariableNames_hadrons_cmssw)
