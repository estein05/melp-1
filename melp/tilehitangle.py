import ROOT
import numpy as np
from melp.libs import mathfunctions as mf


class TileHitAngle():
    def __init__ (self, filename, output):
        self.filename     = filename
        self.output       = output
        self.output_z     = output + "_z"
        self.output_angle = output + "_angle"

        self.result_z     = np.zeros(0)
        self.result_angle = np.zeros(0)

        self.file         = ROOT.TFile(filename)
        self.mu3e_mchits  = self.file.Get("mu3e_mchits")
        self.mu3e         = self.file.Get("mu3e")
        self.sensor       = self.file.Get("alignment/sensors")
        self.tiles        = self.file.Get("alignment/tiles")

        self.tilehit_tile_dic = {}
        self.tile_mc_i        = {}
        self.tile_id_pos      = {}
        self.tile_id_dir      = {}

        # initialize dictionaries
        for i in range(self.mu3e.GetEntries()):
            self.mu3e.GetEntry(i)
            temp_arr_1 = []
            for j in self.mu3e.tilehit_mc_i:
                temp_arr_1.append(j)
            self.tile_mc_i[i] = temp_arr_1

            temp_arr_2 = []
            for j in self.mu3e.tilehit_tile:
                temp_arr_2.append(j)
            self.tilehit_tile_dic[i] = temp_arr_2

        for i in range(self.tiles.GetEntries()):
            self.tiles.GetEntry(i)
            # direction
            xyz = []
            xyz.append(self.tiles.dirx)
            xyz.append(self.tiles.diry)
            xyz.append(self.tiles.dirz)

            self.tile_id_dir[self.tiles.sensor] = xyz

            # position
            tile_xyz = []
            tile_xyz.append(self.tiles.posx)
            tile_xyz.append(self.tiles.posy)
            tile_xyz.append(self.tiles.posz)
            self.tile_id_pos[self.tiles.sensor] = tile_xyz

    #####################
    # private functions #
    #####################

    def __Get_TID_from_Frame_ID (self, mc_i):
        self.mu3e_mchits.GetEntry(mc_i)
        tid = self.mu3e_mchits.tid

        return tid

    # ----
    def __Get_HID_from_MC_I (self, mc_i):
        self.mu3e_mchits.GetEntry(mc_i)
        hid = self.mu3e_mchits.hid

        return hid

    # ----
    def __Get_TID_from_MC_I (self, mc_i):
        self.mu3e_mchits.GetEntry(mc_i)
        tid = self.mu3e_mchits.tid

        return tid

    # ----
    def __Get_Sensor_IDs_from_Frame_ID (self, entry):
        self.mu3e.GetEntry(entry)

        # Get Sensor IDs
        hit_id_arr = []

        sensor_id_arr = []
        for j in self.mu3e.hit_pixelid:
            sensor_id_arr.append(j)

        # Get MC index
        mc_i_arr = []
        for j in self.mu3e.hit_mc_i:
            mc_i_arr.append(j)

        return sensor_id_arr, mc_i_arr

    # ----
    def __Get_Sensor_Pos_from_Pixel_ID (self, pixelid):
        pixel = pixelid >> 16
        self.sensor.GetEntry(pixel)

        row_param = pixel & 0xFF
        col_param = (pixel >> 8) & 0xFF


        sensor_pos_vxyz = []
        sensor_pos_vxyz.append(self.sensor.vx)
        sensor_pos_vxyz.append(self.sensor.vy)
        sensor_pos_vxyz.append(self.sensor.vz)

        sensor_pos_col = []
        sensor_pos_col.append(self.sensor.colx)
        sensor_pos_col.append(self.sensor.coly)
        sensor_pos_col.append(self.sensor.colz)

        sensor_pos_row = []
        sensor_pos_row.append(self.sensor.rowx)
        sensor_pos_row.append(self.sensor.rowy)
        sensor_pos_row.append(self.sensor.rowz)

        pos = np.array(sensor_pos_vxyz) + (col_param+0.5)*np.array(sensor_pos_col) + (row_param+0.5)*np.array(sensor_pos_row)

        return pos

    #####################
    # public  functions #
    #####################

    def hitAngleTID(self, n=0, angle="norm"):

        # counters
        hid_discard = 0
        hid_ok      = 0
        tid_discard = 0
        tid_ok      = 0


        # Check Argument
        if n > len(self.tilehit_tile_dic) or n == 0:
            n = len(self.tilehit_tile_dic)
        print("Frames to analyze: ", n, " of ",  len(self.tilehit_tile_dic))

        # Define Arrays for result
        angle_sensor_tile = []
        z_arr = []

        # loop over all Root frames
        for i in range(n):
        #for i in range(100):
            # loop over all tile hits in one Root frame
            for u in range(len(self.tilehit_tile_dic[i])):

                ##################################
                # HID CHECK
                # only first hit gets analyzed
                ##################################
                tile_id  = self.tilehit_tile_dic[i][u]
                hid_test = self.__Get_HID_from_MC_I(self.tile_mc_i[i][u])
                if hid_test != 1:
                    hid_discard = hid_discard + 1
                    continue
                hid_ok = hid_ok +1


                # loop over all pixel hits in one Root frame

                tile_pos = self.tile_id_pos[tile_id]

                tmp_distance_tile_to_pixel = []
                sensor_ids, sensor_frame_mc_i = self.__Get_Sensor_IDs_from_Frame_ID(i)

                # TID for tile
                tid_tile_test   = self.__Get_TID_from_MC_I(self.tile_mc_i[i][u])

                for v in range(len(sensor_ids)):
                    ##################################
                    # TID CHECK
                    # check for matching sensor and tile hits
                    ##################################
                    tid_sensor_test = self.__Get_TID_from_MC_I(sensor_frame_mc_i[v])
                    if tid_sensor_test != tid_tile_test:
                        tid_discard = tid_discard +1
                        continue
                    tid_ok = tid_ok + 1

                    pixel_id = sensor_ids[v]
                    pixel_pos = self.__Get_Sensor_Pos_from_Pixel_ID(pixel_id)
                    distance  = np.sqrt((tile_pos[0]-pixel_pos[0])**2 + (tile_pos[1]-pixel_pos[1])**2 + (tile_pos[2]-pixel_pos[2])**2)


                    tmp_distance_tile_to_pixel.append(distance)

                ##################################
                # the nearest matching sensor hit is used to approximate the trajectory
                ##################################
                # tmp_distance_tile_to_pixel can be zero!
                if len(tmp_distance_tile_to_pixel) != 0 :
                    index     = np.where(tmp_distance_tile_to_pixel == min(tmp_distance_tile_to_pixel))[0][0]
                    sensor_id = sensor_ids[index]

                    pixel_pos = self.__Get_Sensor_Pos_from_Pixel_ID(sensor_id)

                    vector_sensor_tile = np.array(pixel_pos) - np.array(tile_pos)

                    if angle == "norm":
                        angle_sensor_tile.append(mf.angle_between(vector_sensor_tile, self.tile_id_dir[tile_id]))
                    elif angle == "theta":
                        angle_sensor_tile.append(mf.angle_between(vector_sensor_tile, [0,0,1]))
                    elif angle == "phi":
                        vector = np.cross(self.tile_id_dir[tile_id],np.array([0,0,1]))
                        angle_sensor_tile.append(mf.angle_between(vector_sensor_tile, vector))
                    else:
                        print("ERROR: angle != [norm, theta, phi]")
                    z_arr.append(tile_pos[2])

            # Print progress
            if i % 1000 == 0 and i != 0:
                print(round((i/n)*100,2), "%")
        print("100%")

        print("HID CHECK: ", hid_ok, " of " , hid_ok+ hid_discard, "ok")
        print("TID CHECK: ", tid_ok, " of " , tid_ok+ hid_discard, "ok")
        print("Total Events with matching Tile and Sensor Hit: ", len(z_arr), " of: ", hid_ok, " primary Tile hits")

        self.result_z     = np.array(z_arr)
        self.result_angle = np.array(angle_sensor_tile)

        return self.result_z, self.result_angle


    # ----
    def getResult(self):
        return self.result_z, self.result_angle

    # ----
    def saveTxt(self):
        np.savetxt(self.output_z, self.result_z)
        np.savetxt(self.output_angle, self.result_angle)

    # ----
    def saveCompressed(self):
        np.savez_compressed(self.output, z=self.result_z, angle=self.result_angle)