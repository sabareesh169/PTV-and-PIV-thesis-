class TrainingProcess:
    
    """
    Takes in the loss functions constructed in the Velocity Model.
    Runs an optimizer to minimize the loss function
    """
    
    def __init__(self, ParticleData, VelocityModel):
        self.sess = tf.Session()

        self.ParticleData = ParticleData
        self.VelocityModel = VelocityModel
        self.optimizer_phy = tf.train.AdamOptimizer().minimize(VelocityModel.total_residue, var_list=VelocityModel.vel_weights+VelocityModel.vel_biases)
        self.optimizer_vel = tf.train.AdamOptimizer().minimize(VelocityModel.loss_vel, var_list=VelocityModel.vel_weights+VelocityModel.vel_biases)
        self.optimizer_sigma = tf.train.AdamOptimizer().minimize(VelocityModel.neg_log_prob, var_list=VelocityModel.sigma)
    
        init = tf.global_variables_initializer()
        self.sess.run(init)
        
    def match_particles_and_velocity(self, n_iter):
        """
        :param size: Sampling the points, theta and sigma one after the other for n_iter number of times.
        :returns: optimized weights of the velocity DNN and the matched particles.
        """
        for i in range(n_iter):
            index=sampling_points(self.ParticleData.initial_pos, self.ParticleData.final_pos, self.sess.run(self.VelocityModel.pos_NN), self.ParticleData.cluster, self.sess.run(self.VelocityModel.sigma))
            final_index=self.ParticleData.rescale_pos_data(self.ParticleData.final_pos[index])
            sampling_theta(self, self.optimizer_vel, self.ParticleData.initial_pos, final_index, self.ParticleData.t_initial, self.ParticleData.t_final)
            sampling_sigma(self, self.optimizer_sigma, self.sess.run(self.VelocityModel.pos_NN), final_index)
        self.index=index  

    def train_velocity(self, n_iter):
        """
        :param size: Sampling the theta and sigma one after the other for n_iter number of times.
        :returns: optimized weights of the velocity DNN.
        """
        for i in range(n_iter):
            sampling_theta(self, self.optimizer_vel, self.ParticleData.initial_pos, self.ParticleData.final_pos, self.ParticleData.t_initial, self.ParticleData.t_final)
            sampling_sigma(self, self.optimizer_sigma, self.sess.run(self.VelocityModel.pos_NN), self.ParticleData.final_pos)

    def predict_velocity(self, t, x, y):
        """
        :param : the time and position of the point.
        :returns: velocity at the particular position and time.
        """
        return self.sess.run(                    