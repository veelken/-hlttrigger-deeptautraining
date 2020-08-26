
threshold = 1.e-3

inputVariables_tau_hdf5 = [ 
   5.0000000e+00,  4.8926629e-02,  1.9890189e-01, -6.7454469e-01,
   1.3329468e+00,  2.5407474e-02, -1.0000000e+00,  1.0000000e+00,
   5.0000000e-01, -3.6893645e-01, -4.5074170e+02, -3.4174868e-01,
  -3.3752263e-01,  0.0000000e+00, -1.9312813e+02, -1.9312813e+02,
  -2.5284836e-01,  3.2752464e+00,  1.0000000e+00, -1.4786299e-01,
  -2.8925055e-01,  1.0000000e+00, -8.6498909e-02, -4.9295127e-01,
   7.8944154e-03,  1.0000000e+00, -3.9400792e-01,  1.0828287e-02,
   1.9112147e-02, -1.4851254e-03,  4.0612975e-01,  0.0000000e+00,
   0.0000000e+00,  1.5493211e+00,  4.1327482e-01, -1.4346227e-01,
   1.0000000e+00,  5.9914112e-01,  1.0000000e+00,  9.6177506e-01,
   2.6737967e-01,  6.0556412e-01,  0.0000000e+00,  5.8956593e-01
]

inputVariableNames_tau_hdf5 = [ 
  'rho', 'tau_pt', 'tau_eta', 'tau_phi', 'tau_mass', 'tau_E_over_pt', 'tau_charge',
  'tau_n_charged_prongs', 'tau_n_neutral_prongs', 'chargedIsoPtSum',
  'chargedIsoPtSumdR03_over_dR05', 'footprintCorrection', 'neutralIsoPtSum',
  'neutralIsoPtSumWeight_over_neutralIsoPtSum', 'neutralIsoPtSumWeightdR03_over_neutralIsoPtSum',
  'neutralIsoPtSumdR03_over_dR05', 'photonPtSumOutsideSignalCone', 'puCorrPtSum',
  'tau_dxy_valid', 'tau_dxy', 'tau_dxy_sig',
  'tau_ip3d_valid', 'tau_ip3d', 'tau_ip3d_sig', 'tau_dz', 'tau_dz_sig_valid', 'tau_dz_sig',
  'tau_flightLength_x', 'tau_flightLength_y', 'tau_flightLength_z', 'tau_flightLength_sig',
  'tau_pt_weighted_deta_strip', 'tau_pt_weighted_dphi_strip', 'tau_pt_weighted_dr_signal',
  'tau_pt_weighted_dr_iso', 'tau_leadingTrackNormChi2', 'tau_e_ratio_valid', 'tau_e_ratio',
  'tau_gj_angle_diff_valid', 'tau_gj_angle_diff', 'tau_n_photons', 'tau_emFraction',
  'tau_inside_ecal_crack', 'leadChargedCand_etaAtEcalEntrance_minus_tau_eta'
]

inputVariables_tau_cmssw = [ 5, 0.0489266, 0.198902, -0.674545, 1.33295, 0.0254075, -1, 1, 0.5, -0.368936, -450.742, -0.341749, -0.337523, 0, -193.128, -193.128, -0.252848, 3.27525, 1, -0.147863, -0.289251, 1, -0.0864989, -0.492951, 0.00789442, 1, -0.394008, 0.0108283, 0.0191121, -0.00148513, 0.40613, 0, 0, 1.54932, 0.413275, -0.143462, 1, 0.599141, 1, 0.961775, 0.26738, 0.605564, 0, 0.589566 ]

inputVariableNames_tau_cmssw = [  
  'rho', 'tau_pt', 'tau_eta', 'tau_phi', 'tau_mass', 'tau_E_over_pt', 'tau_charge',
  'tau_n_charged_prongs', 'tau_n_neutral_prongs', 'chargedIsoPtSum',
  'chargedIsoPtSumdR03_over_dR05', 'footprintCorrection', 'neutralIsoPtSum',
  'neutralIsoPtSumWeight_over_neutralIsoPtSum', 'neutralIsoPtSumWeightdR03_over_neutralIsoPtSum',
  'neutralIsoPtSumdR03_over_dR05', 'photonPtSumOutsideSignalCone', 'puCorrPtSum',
  'tau_dxy_valid', 'tau_dxy', 'tau_dxy_sig', 
  'tau_ip3d_valid', 'tau_ip3d', 'tau_ip3d_sig', 'tau_dz', 'tau_dz_sig_valid', 'tau_dz_sig',
  'tau_flightLength_x', 'tau_flightLength_y', 'tau_flightLength_z', 'tau_flightLength_sig',
  'tau_pt_weighted_deta_strip', 'tau_pt_weighted_dphi_strip', 'tau_pt_weighted_dr_signal',
  'tau_pt_weighted_dr_iso', 'tau_leadingTrackNormChi2', 'tau_e_ratio_valid', 'tau_e_ratio',
  'tau_gj_angle_diff_valid', 'tau_gj_angle_diff', 'tau_n_photons', 'tau_emFraction', 
  'tau_inside_ecal_crack', 'leadChargedCand_etaAtEcalEntrance_minus_tau_eta'
]

def compareInputVariables(label, inputVariables_hdf5, inputVariableNames_hdf5, inputVariables_cmssw, inputVariableNames_cmssw):
    if len(inputVariables_hdf5) != len(inputVariables_cmssw):
        raise ValueError("Mismatch in number of input variabes: hdf5 = %i, CMSSSW = %i" % (len(inputVariables_hdf5), len(inputVariables_cmssw)))
    if inputVariableNames_hdf5 and len(inputVariableNames_hdf5) != len(inputVariables_hdf5):
        raise ValueError("Mismatch between hdf5 input variabes and names: variables = %i, names = %i" % (len(inputVariables_hdf5), len(inputVariableNames_hdf5)))
    if inputVariableNames_cmssw and len(inputVariableNames_cmssw) != len(inputVariables_cmssw):
        raise ValueError("Mismatch between CMSSW input variabes and names: variables = %i, names = %i" % (len(inputVariables_cmssw), len(inputVariableNames_cmssw)))

    print("%s:" % label)
    numInputVariables = len(inputVariables_hdf5)
    for idxInputVariable in range(numInputVariables):
        value_hdf5 = inputVariables_hdf5[idxInputVariable]
        value_cmssw = inputVariables_cmssw[idxInputVariable]
        diff = abs(value_hdf5 - value_cmssw)
        mean = 0.5*(abs(value_hdf5) + abs(value_cmssw))
        if diff > (threshold*mean):
            label_hdf5 = "(%s)" % inputVariableNames_hdf5[idxInputVariable] if inputVariableNames_hdf5 else ""
            label_cmssw = "(%s)" % inputVariableNames_cmssw[idxInputVariable] if inputVariableNames_cmssw else ""
            print("Mismatch in variable #%i: hdf5 %s = %1.4f, CMSSW %s = %1.4f" % (idxInputVariable, label_hdf5, value_hdf5, label_cmssw, value_cmssw))

compareInputVariables("tau", inputVariables_tau_hdf5, inputVariableNames_tau_hdf5, inputVariables_tau_cmssw, inputVariableNames_tau_cmssw)
