# -*- coding: utf-8 -*-
"""
Einzel lens simulation code
Scroll down to create a chip of certain dimensions
@author: Mateusz Czajka
"""
import numpy as np
import matplotlib.pyplot as plt
#electron charge (C)
e = 1.602e-19

class Chip:
    """
    A class to represent a Chip object.
    """
    def __init__(self, spacings, aperture_thicknesses, aperture_diameter):
        """
        Parameters
        ----------
        spacings : array of floats
        aperture_thicknesses : array of floats
        aperture_diameter : array of floats

        """

        self.spacings = spacings
        self.aperture_thicknesses = aperture_thicknesses
        self.aperture_diameter = aperture_diameter

    def get_aperture_focal_length(self, V_left, d_left, V_lens, d_right, V_right, base_voltage):
        """Calculates the focal length of a single aperture charged plate based on
        the voltages of the neighbouring plates at voltages V_left and V_right.

        Note 1: this calculation only works for electrons
        (remove the minus sign next to the focal length for protons)

        Note 2: it assumes that electrons arrive at the lens with energy e * (V_lens-base_voltage)"""


        #Parallel plate capacitor E-field
        E_right = (V_right - V_lens) / d_right # >0 if it's an accelerating field
        E_left = (V_lens - V_left) / d_left # >0 if it's an accelerating field

        try:
            return - 4 * (V_lens - base_voltage) / (E_right - E_left)
        except(ZeroDivisionError):
            return np.Inf

    def get_all_focal_lengths(self, voltages):
        """
        Gets focal lengths of all the charged apertures in the system

        Parameters
        ----------
        voltages : array of floats (left to right)
            Aperture voltages

        Returns
        -------
        focal_lengths : array of floats
            focal lengths of all the apertures (left to right)

        """
        focal_lengths = np.zeros((len(self.spacings))) #check

        for aperture_index, spacing in enumerate(self.spacings):

            if aperture_index < len(self.spacings) - 1:
                focal_lengths[aperture_index] = self.get_aperture_focal_length(voltages[aperture_index],
                                                                          spacing,
                                                                          voltages[aperture_index + 1],
                                                                          self.spacings[aperture_index + 1],
                                                                          voltages[aperture_index + 2],
                                                                          voltages[0])
            else:
                #The substrate wafer is assumed: 1. to be grounded  2. to be far away from the system
                focal_lengths[aperture_index] = self.get_aperture_focal_length(voltages[aperture_index],
                                                                          spacing,
                                                                          voltages[aperture_index + 1],
                                                                          np.Inf,
                                                                          0,
                                                                          voltages[0])
        return focal_lengths

    def get_system_focal_length(self, voltages):
        """
        Calculates the "net" focal length of the entire system

        Parameters
        ----------
        voltages : array of floats
            voltages applied to the apertures

        Returns
        -------
        total_focal_length : float

        """
        with np.errstate(all="ignore"):
            total_focal_length = 1 / (np.sum(1 / self.get_all_focal_lengths(voltages)))

            """
            except(ZeroDivisionError):
            print("Electrons were not able to make it through, try tweaking the lens voltages")
            return 0
            """
            return total_focal_length

    def transform_deflection_aperture(self, incident_ray_deflection_angle, incident_ray_offset,
                                      aperture_focal_length):

        outgoing_deflection_angle = incident_ray_deflection_angle - incident_ray_offset / aperture_focal_length

        """The offset approximately stays the same, unless you wanna add some math accounting
        for that. Here we assume that the electron moves so fast through the aperture that it
        does not really displace inside"""
        outgoing_ray_offset = incident_ray_offset
        return outgoing_deflection_angle, outgoing_ray_offset

    def transform_deflection_gap(self, incident_ray_deflection_angle, incident_ray_offset,
                                      bounding_voltages, plate_separation):
        """
        Calculates the deflection and the offset of an electron after crossing a uniform
        E-field(created by a parallel plate capacitor) from left to right,
        assuming paraxial approximation.

        Parameters
        ----------
        incident_ray_deflection_angle : float

        incident_ray_offset : float

        bounding_voltages : array of floats: [left_plate_voltage, right_plate_voltage]

        plate_separation : float

        Returns
        -------
        two floats:
            outgoing deflection angle and offset.

        """
        try:
            outgoing_deflection_angle = incident_ray_deflection_angle * np.sqrt(bounding_voltages[0] /
                                                                                bounding_voltages[1])
        except(ZeroDivisionError):
            print("the electron slowed down to zero!")

        try:
            outgoing_ray_offset = incident_ray_offset + incident_ray_deflection_angle * 2 * plate_separation / (np.sqrt(bounding_voltages[1] / bounding_voltages[0]) + 1)
        except(ZeroDivisionError):
            outgoing_ray_offset = 0
        return outgoing_deflection_angle, outgoing_ray_offset

    def get_all_offsets_and_deflections(self, electron_release_angle, electron_release_offset,
                                        electron_release_energy, voltages):
        deflections, offsets = np.zeros(len(self.spacings)+1), np.zeros(len(self.spacings)+1)
        deflections[0], offsets[0] = electron_release_angle, electron_release_offset

        focal_lengths = self.get_all_focal_lengths(voltages)

        for aperture_index, spacing in enumerate(self.spacings):
            if aperture_index == len(self.spacings): #TODO: Adjust for odd number of spacings!
                break
            else:
                 deflection_before_aperture, offset_before_aperture  = self.transform_deflection_gap(deflections[aperture_index],
                                                                                               offsets[aperture_index],
                                                                                               [voltages[aperture_index] - voltages[0] + electron_release_energy,
                                                                                                voltages[aperture_index + 1] - voltages[0] + electron_release_energy],
                                                                                               spacing)
                 deflections[aperture_index + 1], offsets[aperture_index + 1]  = self.transform_deflection_aperture(deflection_before_aperture,
                                                                                                                offset_before_aperture,
                                                                                                                focal_lengths[aperture_index])
                 if deflections[aperture_index + 1] > 1 or deflections[aperture_index + 1] < -1:
                     print("The paraxial approximation has been violated:")
                     print("Deflection angle encountered: " + str(deflections[aperture_index + 1]) + " rad")

            """
            elif aperture_index%2 == 1:
                deflections[aperture_index], offsets[aperture_index]  = self.transform_deflection_aperture(deflection_before_aperture,
                                                                                                                offset_before_aperture,
                                                                                                                focal_lengths[aperture_index])
            elif aperture_index%2 == 0:
                deflection_before_aperture, offset_before_aperture  = self.transform_deflection_gap(deflections[aperture_index],
                                                                                               offsets[aperture_index],
                                                                                               [voltages[aperture_index] - voltages[0] + electron_release_energy,
                                                                                                voltages[aperture_index + 1] - voltages[0] + electron_release_energy],
                                                                                               spacing)
            """
        return deflections, offsets

    def linear_ray_path(self, deflections, offsets, number_of_datapoints):
        """
        Creates an array of electron position as a function of depth into the
        system (connecting calculated offsets with lines)
        Parameters
        ----------
        deflections : array of floats
            deflections (in rad) at each of the apertures.
        offsets : array of floats
            offsets (in m) at each of the apertures.
        number_of_datapoints : int
            number of datapoints

        Returns
        -------
        x : float array (depth into the system)
        y : float array (offset as a function of x)

        """

        x = np.linspace(0, 1.0005 * np.sum(self.spacings), number_of_datapoints)
        y = []

        distance_into_the_system = 0
        for spacing_index, spacing in enumerate(self.spacings):
            #values = (x[np.where((x >= distance_into_the_system) & (x < distance_into_the_system + spacing))] - distance_into_the_system)* deflections[spacing_index] + np.sum(offsets[offsets <= offsets[spacing_index]])
            values = (x[np.where((x >= distance_into_the_system) & (x < distance_into_the_system + spacing))] - distance_into_the_system) * (offsets[spacing_index + 1] - offsets[spacing_index]) / spacing + offsets[spacing_index]
            y += values.tolist()
            distance_into_the_system += spacing

        #values = x[np.where(x >= distance_into_the_system)] * deflections[spacing_index] + np.sum(offsets[offsets <= offsets[spacing_index]])
        values = (x[np.where((x >= distance_into_the_system))] - distance_into_the_system) * deflections[-1] + offsets[-1]
        y += values.tolist()

        return x, y

    def plot_custom_ray(self, electron_release_angle, electron_release_offset,
                        electron_release_energy, voltages, number_of_datapoints):
        """
        Plots a path of an electron of custom release angle [rad], offset [m]
        and energy [eV]

        Parameters
        ----------
        electron_release_angle : float
            angle in rad
        electron_release_offset : float
            distance in m
        electron_release_energy : float
            energy in eV
        voltages : array of floats
            voltage in volts.
        number_of_datapoints : int

        Returns
        -------
        None. It only plots a single ray

        """
        deflections, offsets = self.get_all_offsets_and_deflections(electron_release_angle, electron_release_offset,
                                        electron_release_energy, voltages)

        x, y = self.linear_ray_path(deflections, offsets, number_of_datapoints)

        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_title('Electron ray trace', fontsize=16)
        ax.set_xlabel(r'distance into the system, [m]', fontsize=13)
        ax.set_ylabel(r'vertical distance, [m]', fontsize=13)
        plt.hlines(0, 0, np.sum(self.spacings), colors='grey', linestyles='solid', label='Optical Axis')
        distance_into_the_system = 0
        for spacing_index, spacing in enumerate(self.spacings):
            distance_into_the_system += spacing
            plt.axvline(x=distance_into_the_system, alpha=0.5, dashes=([2,4,2,4]),label=f"Aperture {spacing_index + 1}, ${voltages[spacing_index]} V$")

        #Cnts
        plt.axvline(x=0, alpha=0.5,color="black")
        plt.axvline(x=0, alpha=0.9, dashes=([1,2,1,2]),color="black")

        ax.plot(x, y, color='green', alpha=0.7, label="Electron ray")
        ax.grid(True, color='grey', dashes=[2,2])
        plt.legend(fontsize=8)
        plt.show()

    #def plot_simulation():
"""
Create your chip like this: Chip([Spacings from left to right],
                                 [aperture thicknesses from left to right]
                                 aperture_diameter)
"""

chip_v0 = Chip([2e-3, 2e-3, 500e-9, 500e-9],
               [50e-9, 50e-9, 50e-9, 50e-9],
               250e-9)

"""
Get your total focal length of the system, input all the voltages applied:
input voltages like this:[CNTs_voltage, first aperture, first_cylinder, second_cylinder, ...]
"""
chip_v0_focal_length = chip_v0.get_system_focal_length([-1000, 0, 0,-1500, 0])
print(chip_v0_focal_length)


"""
Plot custom electron paths, input:(electron_release_angle, electron_release_offset,
                        electron_release_energy, voltages, number_of_datapoints)
"""
#chip_v0.plot_custom_ray(0,0,0,[-1000,0,0,2000,0], 10000) #No deflect
chip_v0.plot_custom_ray(0.001,5e-6,50,[-1000,0,0,2500,0], 10000) #big deflect
chip_v0.plot_custom_ray(0.001,5e-6,50,[-1000,0,0,500,0], 10000) #big deflect 2
#chip_v0.plot_custom_ray(0,-5e-6,0,[-5000,0,2000,0,0], 10000) #check this one!