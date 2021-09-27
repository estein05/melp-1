#---------------------------------------------------------------------
#  DETECTOR CLASS
#       - creates a detecor with tiles and pixel sensors
#  TODO:
#       - add fibre / mmpcs to detecor
#---------------------------------------------------------------------
import ROOT

import pickle
import numpy as np

from melp.src.sensor import Sensor
from melp.src.sensor import SensorModul
from melp.src.tile import Tile
from melp.src.tile import TileDetector
from melp.src.hit import Hit

class Detector():
    def __init__ (self, tiles, sensors, hits = {}):
        #self.Tiles   = tiles
        self.SensorsModules = sensors
        self.TileDetector = tiles

        print("------------------------------")
        print("Detector geometry loaded\n")
        print("Stats:")
        print("  - Tiles: ", len(self.TileDetector.tile))
        print("  - Pixel Modules: ", len(self.SensorsModules.sensor))
        print("------------------------------")

    #-----------------------------------------
    #  Load Detector geometry from Root File
    #-----------------------------------------
    @classmethod
    def initFromROOT (cls, filename):
        file            = ROOT.TFile(filename)
        ttree_sensor    = file.Get("alignment/sensors")
        ttree_tiles     = file.Get("alignment/tiles")

        # TILES
        tile_id_pos      = {}
        tile_id_dir      = {}

        for i in range(ttree_tiles.GetEntries()):
            ttree_tiles.GetEntry(i)
            # direction
            xyz = []
            xyz.append(ttree_tiles.dirx)
            xyz.append(ttree_tiles.diry)
            xyz.append(ttree_tiles.dirz)

            tile_id_dir[ttree_tiles.sensor] = xyz

            # position
            tile_xyz = []
            tile_xyz.append(ttree_tiles.posx)
            tile_xyz.append(ttree_tiles.posy)
            tile_xyz.append(ttree_tiles.posz)
            tile_id_pos[ttree_tiles.sensor] = tile_xyz

        Tiles = {}
        for id in tile_id_pos:
            Tiles[id] = Tile(tile_id_pos[id], tile_id_dir[id], id)

        # PIXEL
        Sensors = {}

        for i in range(ttree_sensor.GetEntries()):
            ttree_sensor.GetEntry(i)
            sensor_pos = np.array([ttree_sensor.vx,ttree_sensor.vy,ttree_sensor.vz])
            sensor_row = np.array([ttree_sensor.rowx,ttree_sensor.rowy,ttree_sensor.rowz])
            sensor_col = np.array([ttree_sensor.colx,ttree_sensor.coly,ttree_sensor.colz])
            Sensors[ttree_sensor.sensor] = Sensor(sensor_pos, sensor_row, sensor_col,ttree_sensor.sensor)
            pass

        return cls(TileDetector(Tiles), SensorModul(Sensors))

    #-----------------------------------------
    #  Load Detector geometry from Save File
    #-----------------------------------------
    @classmethod
    def initFromSave (cls, filename):
        data = []
        with open(filename, "rb") as f:
            for i in pickle.load(f):
                data.append(i)

        return cls(data[0],data[1])
    #-----------------------------------------
    #  private functions
    #-----------------------------------------


    #-----------------------------------------
    #  public functions
    #-----------------------------------------

    #-----------------------------------------

    def save(self, filename):
        data = [self.TileDetector, self.SensorsModules]

        with open(filename, "wb") as f:
            pickle.dump(data, f)


    def addTileHits(self, filename):
        file          = ROOT.TFile(filename)
        ttree_mu3e    = file.Get("mu3e")
        #ttree_mu3e_mc = self.file.Get("mu3e_mchits")
        for frame in range(ttree_mu3e.GetEntries()):
            ttree_mu3e.GetEntry(frame)
            for i in range(len(ttree_mu3e.tilehit_tile)):
                tile = ttree_mu3e.tilehit_tile[i]
                edep = ttree_mu3e.tilehit_edep[i]
                mc_i = ttree_mu3e.tilehit_mc_i[i]


                tilehit = Hit(edep = edep, mc_i = mc_i)
                self.TileDetector.addHit(tile, tilehit)
